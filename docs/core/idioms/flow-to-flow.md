# Running dependent flows

There are many situations where users want to configure dependencies at the flow level; for example,
if you have a data preprocessing flow that you maintain separately from a model training flow, and you 
always want to ensure that the preprocessing flow runs before the training flow.

To support this, Prefect provides a convenient [built-in task for creating Flow runs](/api/latest/tasks/prefect.html#startflowrun)
through the Prefect API.  This task supports:
- triggering flow runs when certain conditions are met in another flow
- providing parameter values that are generated at runtime by another flow
- constructing a Flow-of-Flows that orchestrates and schedules groups of flows simultaneously
- always triggering the most recent version of a flow (so IDs / versions are not hardcoded)
- optionally mirroring the state of the flow run in the task itself
- stable retries to prevent duplication of runs

## Running a parametrized flow

Let's say that you want to always run a flow with parameters that are generated by another flow. 
Naively, you might manually wait for one flow to finish and then manually trigger the next flow to run
with the appropriate parameter values.  Prefect makes this pattern easy to automate via the `StartFlowRun`:


:::: tabs
::: tab Functional API
```python
from prefect import task, Flow
from prefect.tasks.prefect import StartFlowRun


@task
def extract_some_data():
    return {"param-key": "some-random-piece-of-data"}


# assumes you have registered a flow named "example" in a project named "examples"
flow_run = StartFlowRun(flow_name="example", project_name="examples")

with Flow("parent-flow") as flow:
    flow_run(parameters=extract_some_data)
```
:::
::: tab Imperative API
```python
from prefect import Task, Flow
from prefect.tasks.prefect import StartFlowRun


class ExtractSomeData(Task)
    def run(self):
        return {"param-key": "some-random-piece-of-data"}

extract_some_data = ExtractSomeData(name="extract_some_data")

# assumes you have registered a flow named "example" in a project named "examples"
flow_run = StartFlowRun(flow_name="example", project_name="examples")

with Flow("parent-flow") as flow:
    flow_run.set_upstream(extract_some_data, key="parameters")
```
:::
::::

## Scheduling a Flow-of-Flows

Oftentimes different people are responsible for maintaining different flows; in this case it can be useful
to construct a Flow-of-Flows that specifies stateful dependencies between various Flows.  The `wait` kwarg
allows you to specify that the task should wait until the triggered flow run completes, and reflect the
flow run state as the task state.

The following example creates the following Flow-of-Flows that runs every weekday:

![Flow of Flows](/idioms/flow-of-flows.png)

:::: tabs
::: tab Functional API
```python
from prefect import Flow
from prefect.schedules import CronSchedule
from prefect.tasks.prefect import StartFlowRun


weekday_schedule = CronSchedule(
    "30 9 * * 1-5", start_date=pendulum.now(tz="US/Eastern")
)


# assumes you have registered the following flows in a project named "examples"
flow_a = StartFlowRun(flow_name="A", project_name="examples", wait=True)
flow_b = StartFlowRun(flow_name="B", project_name="examples", wait=True)
flow_c = StartFlowRun(flow_name="C", project_name="examples", wait=True)
flow_d = StartFlowRun(flow_name="D", project_name="examples", wait=True)

with Flow("parent-flow", schedule=weekday_schedule) as flow:
    b = flow_b(upstream_tasks=[flow_a])
    c = flow_c(upstream_tasks=[flow_a])
    d = flow_d(upstream_tasks=[b, c])
```
:::

::: tab Imperative API
```python
from prefect import Flow
from prefect.schedules import CronSchedule
from prefect.tasks.prefect import StartFlowRun


weekday_schedule = CronSchedule(
    "30 9 * * 1-5", start_date=pendulum.now(tz="US/Eastern")
)


# assumes you have registered the following flows in a project named "examples"
flow_a = StartFlowRun(flow_name="A", project_name="examples", wait=True)
flow_b = StartFlowRun(flow_name="B", project_name="examples", wait=True)
flow_c = StartFlowRun(flow_name="C", project_name="examples", wait=True)
flow_d = StartFlowRun(flow_name="D", project_name="examples", wait=True)

with Flow("parent-flow", schedule=weekday_schedule) as flow:
    flow_b.set_upstream(flow_a)
    flow_c.set_upstream(flow_a)
    flow_d.set_upstream(flow_b)
    flow_d.set_upstream(flow_c)
```
:::
::::
