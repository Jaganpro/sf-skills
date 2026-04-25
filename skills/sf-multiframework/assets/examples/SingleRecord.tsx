/**
 * Recipe: Single Record
 *
 * Queries a single Account by ID using the Data SDK.
 * Demonstrates the inline gql pattern and the { value } UIAPI shape.
 */

import { useEffect, useState } from "react";
import { createDataSDK, gql } from "@salesforce/sdk-data";

const QUERY = gql`
  query SingleAccount {
    uiapi {
      query {
        Account(first: 1) {
          edges {
            node {
              Id
              Name { value }
              Industry { value }
              BillingCity { value }
            }
          }
        }
      }
    }
  }
`;

interface AccountFields {
  id: string;
  name: string;
  industry: string | null;
  city: string | null;
}

export default function SingleRecord() {
  const [account, setAccount] = useState<AccountFields | undefined>();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const sdk = await createDataSDK();
        const res = await sdk.graphql?.(QUERY);
        // UI API wraps every field in { value } — this is Salesforce-specific.
        const node = res?.data?.uiapi?.query?.Account?.edges?.[0]?.node;
        if (node) {
          setAccount({
            id: node.Id,
            name: node.Name?.value ?? "—",
            industry: node.Industry?.value ?? null,
            city: node.BillingCity?.value ?? null
          });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Request failed");
      }
    })();
  }, []);

  if (error) return <ErrorState message={error} />;
  if (!account) return <Skeleton />;
  return <AccountTile account={account} />;
}

function Skeleton() {
  return <div className="slds-card slds-is-loading">Loading…</div>;
}

function ErrorState({ message }: { message: string }) {
  return <div className="slds-text-color_error">{message}</div>;
}

function AccountTile({ account }: { account: AccountFields }) {
  return (
    <article className="slds-card slds-p-around_medium">
      <h2 className="slds-text-heading_small">{account.name}</h2>
      <p>{account.industry ?? "Unknown industry"}</p>
      {account.city && <p className="slds-text-body_small">{account.city}</p>}
    </article>
  );
}
