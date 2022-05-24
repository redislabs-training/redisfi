
## Investments - RediSearch+JSON
The first portion of the demo looks to create a consumer investment portal (think a cross between Robinhood and your Retirement account).  On every page, the prices are live and change as they update to reflect market changes.

- Navigate first to the [Overview Page]($APP_URL/overview).  It shows 4 different portfolio components.  You can click into each one to see details about that investment category.
- Inside, for example, the [Retirement Fund]($APP_URL/fund/retire2050), you can see a collection of assets and their history.  
- You can click in deeper to look at an individual asset, like [Tesla]($APP_URL/asset/tsla) or [Bitcoin]($APP_URL/asset/btcusd).  On the individual asset view there is a live updating view. **Note:** Occasionally, the live graph will break, a hard refresh of the page will usually fix it.
- You can also use the search bar to search the metadata of the assets as well.

## Research - Vector Similarity Search
The second portion of the demo showcases Vector Similarity Search with 2.2 Million Paragraphs from US Security and Exchange Commission (SEC) 10K+Q documents.  These documents are required to be perodically filed by public and some private companies in the US.

- This portion of the demo starts on the [Research Page]($APP_URL/research)
- There are a few canned "trending" searches and reports.  You can try them, or type in your own.
- The search drop down in this section has 2 options `Full-Text` and `Semantic` Search.
    - `Full-Text` is the "classic" RediSearch, which looks for exact matches of the word or phrase provided.
    - `Semantic` search turns the search term into a vector that is then compared to the paragraph vectors.  This vectorization process translates the words to a binary representation of the "meaning" of the phrase.  This allows it to match a much broader range of things.  That's the general premise of this demo and Vector Similarity Search as a whole.
- The search results show the paragraph matched, and links back to the original document on the SEC website.
- If you click on the `Details` button, it opens a side panel that shows more information about the search results and allows you to filter the results down.
    - This Filter creates a "Hybrid Query" that combines the Full-Text and Semantic search capability in a single query.
    - **Note:** This feature is pretty buggy.  Find a path that works before you show the demo.
