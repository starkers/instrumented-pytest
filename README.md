# pytest

handy URLS:
> see a live preview of the browers
  http://localhost:4444/grid/admin/live

> see the dashboard (videos+logs) of completed sessions
  http://localhost:4444/dashboard/

> push-gateway (received metrics from our pytest app)
  http://localhost:9091
  http://localhost:9091/metrics (raw metrics)

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

1. install virtualenv
`make deps`

2. `direnv allow` ... or... `source venv/bin/activate`

3. install the `pytest-prom` I'm playing with
`pip install  pytest-prom/`

4. launch the support containers

`docker-compose up`

5. run a test
you can skipp the launcher.py and just run pytest..
First however u need to seed a config-file that the launcher creates..

first create `config.yaml` like this:
```
---
hub_url: http://localhost:4444/wd/hub
name: my-suffix
now: 2019-05-24 09:55:41.219340
```

  ``pytest ./tests  --prometheus-pushgateway-url http://localhost:9091 --prometheus-metric-prefix abc_  --prometheus-job-name zalenium --prometheus-extra-label foo=waz``
