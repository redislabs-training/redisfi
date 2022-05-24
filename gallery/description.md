
# Description
RedisFI was built for RedisDays22.  It has 2 parts, an investment banking portion which shows RediSearch+JSON and live data streaming, and a research portal which shows Vector Similarity Search over 10K+Q documents.

The demo starts with a landing page, a good place to do any setup talk you want.  Clicking the `Get Started` button will take you to the beginning of the investment banking portion.  From there, you're able to click into different parts of the portfolio down to individual assets.  All prices show live updates, and on the individual assets you have the ability to see a live price graph.  The search bar will search full text the data we have from the companies.

Click the `Research` link at the top to get into the second portion of the demo.  The landing page here shows some "trending" searches and reports.  You can click the document icon to see the actual report used on the SEC site.  On this portion of the demo, you have two kinds of search: full text and semantic.  Full text search only matches specific terms, whereas the semantic search matches similarly meaning words and phrases.  In the demo for Redis Days, we used the term `scary terms ahead`, which obviously doesn't match any reports in the text search, but has surprisingly relevant matches in the semantic search.  Try your own searches and see what you can find!

# Configuration
There is one external dependancy that requires a sign up before the demo can be run.  It is part of how we pull the historic data required for the demo, and how we're providing actual live price updates into the application.

- Navigate to [alpaca.markets](https://alpaca.markets)
- Click the Sign Up button and enter in your email and a password.
- Go to your email and click the `Confirm My Account` button.
- Login with the email/password combo from earlier
- This should take you to the `Live Trading` console.  Click the `Live Trading` drop down and click into the paper account.  This [link](https://app.alpaca.markets/paper/dashboard/overview) should take you there after you're logged in.
- On the bottom right there's a `Your API Keys` box.  Click `View` and then click the `Generate New` button.  It should show you an API key and Secret Key.  Copy those into the configuration panel below.  You can either come back here to regenerate new ones, or save those to use for future deployments. 