import graphql
import graphql.execution
import inspect
import json
import logging
import sys
import tornado.escape
import tornado.httputil
import tornado.web
import tornado.websocket
import traceback
import typing

from ..http.handler import ApiHandler, WebSocketApiHandler

logger = logging.getLogger(__name__)


class BaseSchemaHander(ApiHandler):
    def get(self):
        schema = self.server_context.graphene_schema.graphql_schema
        schema_str = graphql.print_schema(schema)
        self.set_cookie("Content-Type", "application/graphql")
        self.write(schema_str)


class ApolloSandboxHandler(ApiHandler):
    def get(self):
        self.set_cookie("Content-Type", "text/html")
        self.write("""
        <html>
            <body style="margin: 0;">
                <div style="width: 100%; height: 100%;" id='embedded-sandbox'></div>
                <script src="https://embeddable-sandbox.cdn.apollographql.com/_latest/embeddable-sandbox.umd.production.min.js"></script> 
                <script>
                    new window.EmbeddedSandbox({
                        target: '#embedded-sandbox',
                        initialEndpoint: 'http://localhost/graphql',
                        includeCookies: false,
                    });
                </script>
            </body>
        </html>
        """)


class ExecutionError(Exception):
    def __init__(self, status_code, errors):
        self.status_code = status_code
        self.errors = [str(e) for e in errors]
        self.message = "\n".join(self.errors)


class GraphQLMixin(ApiHandler):
    @property
    def pretty(self):
        return self.context.env.debug

    @property
    def graphene_schema(self):
        return self.context.graphene_schema

    @property
    def graphql_schema(self):
        return self.graphene_schema.graphql_schema

    def extract_gql_params(self, payload: typing.Dict):
        query = payload.get("query")
        variables = payload.get("variables")
        if isinstance(variables, str):
            variables = tornado.escape.json_decode(variables)
        operation_name = payload.get("operationName")
        if operation_name == "null":
            operation_name = None
        return query, variables, operation_name

    def execution_result_to_dict(self, execution_result: graphql.ExecutionResult):
        result_dict = {}
        if execution_result.errors:
            result_dict["errors"] = [self.format_error(e) for e in execution_result.errors]
        result_dict["data"] = execution_result.data
        return result_dict

    def format_error(self, error: typing.Any):
        if isinstance(error, graphql.GraphQLError):
            return graphql.error.graphql_error.format_error(error)
        else:
            return {"message": str(error)}

    @property
    def root_value(self):
        return self

    @property
    def graphql_context(self):
        return None


class BaseGraphQLHandler(GraphQLMixin, ApiHandler):
    async def post(self):
        try:
            await self._run()
        except Exception as ex:
            self._handle_error(ex)

    async def _run(self):
        result, status_code = await self._get_response()
        # self.set_status(status_code)
        self.set_header("Content-Type", "application/json")
        self.write(result)
        await self.finish()

    def _parse_request(self):
        content_type = self.request.headers.get("Content-Type", "text/plain").split(";")[0]
        if content_type != "application/json":
            raise tornado.web.HTTPError(400, "Unsupported content type")
        
        try:
            request_str = tornado.escape.to_unicode(self.request.body)
        except Exception as e:
            raise ExecutionError(400, [e])
        
        try:
            request_json = tornado.escape.json_decode(request_str)
        except (TypeError, ValueError) as e:
            raise tornado.web.HTTPError(400, "Invalid JSON in request body")
        
        return request_json

    async def _get_response(self):
        gql_request = self._parse_request()
        query, variables, operation_name = self.extract_gql_params(gql_request)
        execution_result, valid = self._execute_gql(query, variables, operation_name)
        if execution_result.errors:
            for error in execution_result.errors:
                if error.original_error and not isinstance(error.original_error, graphql.GraphQLError):
                    logger.exception(error.original_error, exc_info=error.original_error)
        status_code = 200
        response = None
        if execution_result is not None:
            if inspect.isawaitable(execution_result) or inspect.iscoroutinefunction(execution_result):
                execution_result = await execution_result
            if hasattr(execution_result, "get"):
                execution_result = execution_result.get()
            response = self.execution_result_to_dict(execution_result)
            if not valid:
                status_code = 400
                del response["data"]
            if self.pretty:
                response = json.dumps(response, indent=2)
            else:
                response = tornado.escape.json_encode(response)
        return response, status_code

    def _execute_gql(self, query, variables, operation_name):
        if not query:
            raise tornado.web.HTTPError(400, "All GraphQL requests must contain a query")

        try:
            document = graphql.parse(query)
        except graphql.GraphQLError as e:
            return graphql.execution.ExecutionResult(errors=[e], data=None), False

        try:
            validation_errors = graphql.validate(self.graphql_schema, document)
        except graphql.GraphQLError as e:
            return graphql.execution.ExecutionResult(errors=[e], data=None), False
        if validation_errors:
            return graphql.execution.ExecutionResult(errors=validation_errors, data=None,), False

        try:
            result = graphql.execute(
                schema=self.graphql_schema,
                document=document,
                root_value=self.root_value,
                context_value=self.graphql_context,
                variable_values=variables,
                operation_name=operation_name)
            return result, True
        except graphql.GraphQLError as e:
            return graphql.execution.ExecutionResult(errors=[e], data=None), False

    def _handle_error(self, e: Exception):
        if not isinstance(e, (tornado.web.HTTPError, ExecutionError, graphql.GraphQLError)):
            tb = "".join(traceback.format_exception(*sys.exc_info()))
            logger.error(f"GraphQL error {e} {tb}")
        errors = None
        if isinstance(e, ExecutionError):
            # self.set_status(400)
            errors = [{"message": e} for e in e.errors]
        elif isinstance(e, graphql.GraphQLError):
            # self.set_status(400)
            errors = [graphql.error.graphql_error.format_error(e)]
        elif isinstance(e, tornado.web.HTTPError):
            # self.set_status(e.status_code)
            errors = [{"message": e.log_message}]
        else:
            # self.set_status(500)
            errors = [{"message": "Internal server error"}]
        error_json = tornado.escape.json_encode({"errors": errors})
        self.write(error_json)


class BaseGraphQLSubscriptionHandler(GraphQLMixin, WebSocketApiHandler):
    operations: typing.Dict[str, typing.AsyncIterator[graphql.execution.ExecutionResult]]
    auth_token: str|None = None

    SUBPROTOCOL = "graphql-transport-ws"
    def select_subprotocol(self, subprotocols: typing.List[str]):
        if self.SUBPROTOCOL in subprotocols:
            return self.SUBPROTOCOL

    def open(self):
        self.operations = {}

    def _subscribe(self, id: str, async_iterator: typing.AsyncIterator[graphql.execution.ExecutionResult]):
        if id in self.operations:
            raise Exception("Operation already exists")
        self.operations[id] = async_iterator

    def _unsubscribe(self, id: str):
        async_iterator = self.operations.pop(id)
        if hasattr(async_iterator, "dispose"):
            async_iterator.dispose()

    def _unsubscribe_all(self):
        for id in self.operations.keys():
            self._unsubscribe(id)

    async def on_message(self, message):
        parsed_message: dict = tornado.escape.json_decode(message)
        operation_id: str = parsed_message.get("id")
        operation_type: str = parsed_message.get("type")
        payload: dict = parsed_message.get("payload")
        match operation_type:
            case "connection_init":
                await self._handle_connection_init(payload)
            case "ping":
                await self._handle_ping(payload)
            case "subscribe":
                await self._handle_subscribe(operation_id, payload)
            case "complete":
                await self._handle_complete(operation_id)

    def try_authenticate(self, token: str):
        pass

    async def _handle_connection_init(self, payload: dict):
        self.auth_token = payload.get("authToken")
        return await self._send_message(None, "connection_ack", None)

    async def _handle_ping(self, payload: dict):
        return await self._send_message(None, "pong", None)

    async def _handle_subscribe(self, operation_id: str, payload: dict):
        query, variables, operation_name = self.extract_gql_params(payload)
        execution_result = await self.graphene_schema.subscribe(
            query=query,
            root_value=self.root_value,
            context_value=self.graphql_context,
            variable_values=variables,
            operation_name=operation_name,
        )
        self._subscribe(operation_id, execution_result)
        if isinstance(execution_result, graphql.execution.ExecutionResult):
            if execution_result.errors:
                return await self._send_errors(operation_id, execution_result.errors)
            else:
                await self._send_next(operation_id, execution_result.data)
        try:
            if hasattr(execution_result, "__aiter__"):
                async for item in execution_result:
                    if operation_id not in self.operations:
                        return
                    assert isinstance(item, graphql.execution.ExecutionResult)
                    await self._send_next(operation_id, item)
            elif inspect.isawaitable(execution_result):
                execution_result = await execution_result
                await self._send_next(operation_id, execution_result)
        except Exception as e:
            await self._send_errors(operation_id, [e])
            self._unsubscribe(operation_id)
            return
        await self._send_complete(operation_id)
        self._unsubscribe(operation_id)

    async def _handle_complete(self, operation_id: str, payload: dict):
        self._unsubscribe(operation_id)

    async def _send_message(self, id: str|None, type: str|None, payload: typing.Any|None):
        message = {}
        if id is not None:
            message["id"] = id
        if type is not None:
            message["type"] = type
        if payload is not None:
            if isinstance(payload, graphql.execution.ExecutionResult):
                payload = self.execution_result_to_dict(payload)
            message["payload"] = payload
        message_str = tornado.escape.json_encode(message)
        await self.write_message(message_str)

    async def _send_next(self, id: str, result: graphql.execution.ExecutionResult):
        return await self._send_message(id, "next", result)

    async def _send_errors(self, id: str, errors: typing.List[graphql.GraphQLError]):
        return await self._send_message(id, "error", [self.format_error(e) for e in errors])

    async def _send_complete(self, id: str):
        return await self._send_message(id, "complete", None)

    def on_close(self):
        self._unsubscribe_all()
