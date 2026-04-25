/**
 * Strict-by-default GraphQL wrapper around the Data SDK.
 *
 * Use this for production code that wants type-safe call sites.
 * Recipes should use inline gql + sdk.graphql?.() directly so the lesson
 * is visible in the recipe file.
 *
 * Strategy variants (see references/error-handling.md):
 *   - Strict      — fail on any error
 *   - Tolerant    — log errors, return partial data
 *   - Permissive  — only fail when no data at all (mutations)
 */

import { createDataSDK } from "@salesforce/sdk-data";
export { gql } from "@salesforce/sdk-data";

let sdkPromise: ReturnType<typeof createDataSDK> | null = null;

function getSdk() {
  if (!sdkPromise) {
    sdkPromise = createDataSDK({
      webapp: {
        on401: () => {
          // Customize: refresh session, redirect to login, etc.
          console.warn("Session expired (401)");
        },
        on403: () => {
          console.warn("Insufficient permissions (403)");
        }
      }
    });
  }
  return sdkPromise;
}

export async function executeGraphQL<TData, TVars = Record<string, unknown>>({
  query,
  variables
}: {
  query: string;
  variables?: TVars;
}): Promise<TData> {
  const sdk = await getSdk();
  const response = await sdk.graphql?.(query, variables);

  if (!response) {
    throw new Error("GraphQL surface unavailable in this environment");
  }
  if (response.errors?.length) {
    throw new Error(response.errors.map((e: { message: string }) => e.message).join("; "));
  }
  return response.data as TData;
}

export async function executeGraphQLTolerant<TData, TVars = Record<string, unknown>>({
  query,
  variables
}: {
  query: string;
  variables?: TVars;
}): Promise<TData> {
  const sdk = await getSdk();
  const response = await sdk.graphql?.(query, variables);

  if (!response?.data) {
    throw new Error("No data returned");
  }
  if (response.errors?.length) {
    console.warn("GraphQL partial errors:", response.errors);
  }
  return response.data as TData;
}

export async function executeGraphQLPermissive<TData, TVars = Record<string, unknown>>({
  query,
  variables
}: {
  query: string;
  variables?: TVars;
}): Promise<TData> {
  const sdk = await getSdk();
  const response = await sdk.graphql?.(query, variables);

  if (!response) {
    throw new Error("GraphQL surface unavailable");
  }
  if (!response.data && response.errors?.length) {
    throw new Error(response.errors.map((e: { message: string }) => e.message).join("; "));
  }
  return response.data as TData;
}
