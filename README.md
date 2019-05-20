# pytest

handy URLS:
> see a live preview of the browers
  http://localhost:4444/grid/admin/live

> see the dashboard (videos+logs) of completed sessions
  http://localhost:4444/dashboard/

> push-gateway (received metrics from our pytest app)
  http://localhost:9091

> prometheus (explore the data it has scraped from push-gateway)
  http://localhost:9090/graph

  (http://localhost:9090/targets to ensure it is scraping targets)

taking a stab at: selenium+pytest+prometheus metrics.

Goal:
- ordered testing
- push metrics at end (or scrape optional maybe?)
- timed looping?
- runBefore/runAfter
- zalenium specific stuff for marking test status
- result proc (upload + slack?)


# running locally

  launch with:
  `docker-compose up`
