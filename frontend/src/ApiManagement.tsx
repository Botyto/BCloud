import React, { useEffect, useState } from 'react';
import { ApolloClient, InMemoryCache, ApolloProvider, HttpLink, split, ApolloLink, concat, NormalizedCacheObject } from '@apollo/client';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';
import { getMainDefinition } from '@apollo/client/utilities';
import { persistCache, LocalStorageWrapper  } from 'apollo3-cache-persist';
import OfflineLink from 'apollo-link-offline';
import Loading from './components/Loading';

function ApiManagement(props: any) {
	const SERVER_HOST = import.meta.env.VITE_BACKEND_URL;
	const [client, setClient] = useState<ApolloClient<NormalizedCacheObject>|null>(null);
	
	useEffect(() => {
		const cache = new InMemoryCache({
			typePolicies: {},
		});
		
		const httpLink = new HttpLink({
			uri: `${SERVER_HOST}/api/graphql`,
			fetchOptions: {
				crossOriginIsolated: false,
			}
		});
		
		const offlineLink = new OfflineLink({
			storage: localStorage,
			sequential: true,
		});
		
		const authMiddleware = new ApolloLink((operation, forward) => {
			// add the authorization to the headers
			operation.setContext(({ headers = {} }) => {
				if ('authorization' in headers) {
					return { headers };
				}
				const token = localStorage.getItem("authentication-token");
				if (!token || token === "") {
					return { headers };
				}
				return {
					headers: {
						...headers,
						authorization: "Bearer " + token,
					}
				};
			});
			return forward(operation);
		});
		
		const wsLink = new GraphQLWsLink(createClient({
			url: `ws://${SERVER_HOST}/api/graphql/subscription`,
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
			//concat(authMiddleware, ApolloLink.from([offlineLink, httpLink])),
		);

		const client = new ApolloClient({
			cache: cache,
			link: link,
		});
	
		/*persistCache({
			cache,
			storage: new LocalStorageWrapper(localStorage),
			trigger: 'background',
		}).then(() => setClient(client))
	
		offlineLink.setup(client);*/
		setClient(client);
	
		return () => {};
	}, []);

	if (client === null) {
		return <Loading/>;
	} else {
		return (
			<ApolloProvider client={client}>
				{props.children}
			</ApolloProvider>
		);
	}
}

export { ApiManagement };
