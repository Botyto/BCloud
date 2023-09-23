import React from 'react';
import { ApolloClient, InMemoryCache, ApolloProvider, HttpLink, split, ApolloLink, concat } from '@apollo/client';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';
import { getMainDefinition } from '@apollo/client/utilities';
import { persistCache, LocalStorageWrapper  } from 'apollo3-cache-persist';

const SERVER_HOST = 'localhost:8080';

const cache = new InMemoryCache({
	typePolicies: {},
});

const httpLink = new HttpLink({
	uri: `http://${SERVER_HOST}/graphql`,
	fetchOptions: {
		crossOriginIsolated: false,
	}
});

const authMiddleware = new ApolloLink((operation, forward) => {
	// add the authorization to the headers
	operation.setContext(({ headers = {} }) => {
		if ('authorization' in headers) {
			return { headers };
		}
		return {
			headers: {
				...headers,
				authorization: 'Bearer ' + localStorage.getItem('authentication-token') || null,
			}
		};
	});
	return forward(operation);
});

const wsLink = new GraphQLWsLink(createClient({
	url: `ws://${SERVER_HOST}/graphql/subscription`,
	connectionParams: () => {
		return {
			authToken: localStorage.getItem('authentication-token'),
		};
	},
}));

const link = split(
	({ query }) => {
	const definition = getMainDefinition(query);
	return (
		definition.kind === 'OperationDefinition' &&
		definition.operation === 'subscription'
	);
	},
	wsLink,
	concat(authMiddleware, httpLink),
);

/*persistCache({
	cache,
	storage: new LocalStorageWrapper(localStorage),
})*/

const client = new ApolloClient({
	cache: cache,
	link: link,
});

function ApiManagement(props: any) {
	return (
		<ApolloProvider client={client}>
			{props.children}
		</ApolloProvider>
	);
}

export { ApiManagement, client };
