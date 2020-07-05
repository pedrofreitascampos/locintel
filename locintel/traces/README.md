# trace-tools

Tools supporting the processing and handling of trace (GPS) data:
 * Loading
 * Filtering
 * Sampling

## Common datamodel
* Trace and Probe objects providing unified datamodel

## Loaders
* Single, simple, streaming interface for trace loaders
* Hides all underlying technology complexity

```
from traces.loaders import DruidLoader

druid_config = {
    'url': 'https://fakeurl.com', 
    'endpoint': '/endpoint/v1', 
    'datasource': 'datasource', 
    'username': 'user',
    'password': 'password'
}

traces = DruidLoader(**druid_config).load()
trace = next(traces)
```

NOTE: Credentials can be passed to Loader or inferred from system envs.

## Filters
* Different filtering policies which can be chained to produce cleaner data sets, e.g.:
    * Filter if time gap between probes too big
    * Filter if probe confidence too low
    
```
from traces.filters import LowConfidenceFilter

traces = DruidLoader(**config).load()
filter_policy = LowConfidenceFilter(min_confidence=0.5).filter

filtered_traces = filter(filter_policy, traces)
```

## Sampling
* Re-samples traces according to given policy

```
from traces.samples import SimpleSampler

trace = next(DruidLoader(**config).load())
resampled_trace = SimpleSampler(period=5).sample(trace
```
