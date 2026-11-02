# Runbook: Logging failure scenario

## 1. What occured
An on-call operator or developer receives an automated system alert or notices a steep rise in HTTP 504 (Gateway Timeout) or HTTP 500 exceptions occurring on the `/matches/sync/` endpoint. Users notice match data updates are freezing on the frontend dashboard. In this context, freezing means that the webpage is not up-to-date on current matches and league standings

## 2. How to Confirm the Diagnosis
1. Open your terminal or log management interface tracking the production Django logs.
2. Run a filter search query targeting errors in the match views pipeline:
   `level:"ERROR" AND logger:"matches.views"`
3. Locate the specific Identification token that correlated to the server not running. From here Locate all tokens with tokens with the same value and compile them together to observe why the issue occurred
4. **Confirmation Criteria: ** If the sequence displays `Initiating external sports API match sync` followed by an explicit `TimeoutError` citing the respective API service link, the issue resides entirely with our upstream third-party data provider, not our internal database.

## 3. Remediation Action Plan
1. Verify the current API provider is up and running at their respective webpage
2. If the external status portal confirms a degradation, toggle our fallback switch to use pre-cached historical match data:
   * Open your server environment profile file (`.env`).
   * Change `USE_LIVE_MATCH_FEED=True` to `USE_LIVE_MATCH_FEED=False`.
3. Force restart the application server to clear out bad states
