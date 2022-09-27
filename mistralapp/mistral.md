# Thiết kế của OpenStack DBaaS Scheduler

## Công nghệ sử dụng

- APScheduler

## Xây dựng cơ chế backup định kỳ cho các DB Instance

### Bài toán

Trên một cloud Region có nhiều DB Instance, mỗi DB Instance có thể bật hoặc tắt tính năng tự động Backup định kỳ. Khi tính năng tự động Backup định kỳ được bật, một DB Instance có thể được backup định kỳ theo ngày/theo tuần/theo tháng Cần có một cơ chế cho phép đến đúng giờ đã thiết lập trên DB Instance thì thực chiện chạy job backup cho DB Insatnce.

### Giải pháp hiện tại

Trên Database của service openstack-dbaas có một table backup_policy với các trường sau:

```log
    uuid
    DB_Instance_ID
    Enable: True/False
    Backup_schedule: Theo unix cron format. VD: 2 4 * * mon - 04:02 on every Monday
    Next execution time: Thời điểm tiếp theo job này được thực hiện
```

Định kỳ x phút 1 lần (x=5,10....) hệ thống sẽ thực hiện chạy job spawn_backup_db_instance_jobs. Job này thực hiện lấy toàn bộ các record trong table backup_policy, để check xem job backup của DB Instance trong record có đến thời điểm chạy hay không

Nếu có job đến thời điểm chạy (compare giá trị curent datetime >= next_execution_time), thì spawn_backup_db_instance_jobs đặt job backup_database_instance vào message queue, job sẽ được job worker consume và thực hiện backup cho db instance

Sau đó, sử dụng thư viện croniter https://github.com/kiorky/croniter để update lại next_execution_time của job nếu cần

```python
>>> from croniter import croniter
>>> from datetime import datetime
>>> base = datetime(2010, 1, 25, 4, 46)
>>> iter = croniter('*/5 * * * *', base)  # every 5 minutes
>>> print(iter.get_next(datetime))   # 2010-01-25 04:50:00
```

Ý tưởng lấy từ cơ chế sinh job của mistral

### Cơ chế hoạt động của Mistral

https://github.com/openstack/mistral/blob/stable/yoga/mistral/services/triggers.py#L32


```python
def create_cron_trigger(name, workflow_name, workflow_input,
                        workflow_params=None, pattern=None, first_time=None,
                        count=None, start_time=None, workflow_id=None):
    if not start_time:
        start_time = datetime.datetime.utcnow()

    if isinstance(first_time, str):
        try:
            first_time = datetime.datetime.strptime(
                first_time,
                '%Y-%m-%d %H:%M'
            )
        except ValueError as e:
            raise exc.InvalidModelException(str(e))

    validate_cron_trigger_input(pattern, first_time, count)

    if first_time:
        next_time = first_time

        if not (pattern or count):
            count = 1
    else:
        next_time = get_next_execution_time(pattern, start_time)

    with db_api.transaction():
        wf_def = db_api.get_workflow_definition(
            workflow_id if workflow_id else workflow_name
        )

        wf_spec = parser.get_workflow_spec_by_definition_id(
            wf_def.id,
            wf_def.updated_at
        )

        # TODO(rakhmerov): Use Workflow object here instead of utils.
        eng_utils.validate_input(
            wf_spec.get_input(),
            workflow_input,
            wf_spec.get_name(),
            wf_spec.__class__.__name__
        )

        trigger_parameters = {
            'name': name,
            'pattern': pattern,
            'first_execution_time': first_time,
            'next_execution_time': next_time,
            'remaining_executions': count,
            'workflow_name': wf_def.name,
            'workflow_id': wf_def.id,
            'workflow_input': workflow_input or {},
            'workflow_params': workflow_params or {},
            'scope': 'private'
        }

        security.add_trust_id(trigger_parameters)

        try:
            trig = db_api.create_cron_trigger(trigger_parameters)
        except Exception:
            # Delete trust before raising exception.
            security.delete_trust(trigger_parameters.get('trust_id'))
            raise

    return trig
```

Mistral đầu tiên tạo một background process, định kỳ 1 phút 1 lần run method `process_cron_triggers_v2`

```python
def setup():
    tg = threadgroup.ThreadGroup()
    pt = MistralPeriodicTasks(CONF)

    ctx = auth_ctx.MistralContext(
        user_id=None,
        project_id=None,
        auth_token=None,
        is_admin=True
    )

    tg.add_dynamic_timer(
        pt.run_periodic_tasks,
        initial_delay=None,
        periodic_interval_max=1,
        context=ctx
    )

    _periodic_tasks[pt] = tg

    return tg

```

```python

class MistralPeriodicTasks(periodic_task.PeriodicTasks):

    def __init__(self, conf):
        super(MistralPeriodicTasks, self).__init__(conf)

        periodic_task_ = periodic_task.periodic_task(
            spacing=CONF.cron_trigger.execution_interval,
            run_immediately=True,
        )
        self.add_periodic_task(periodic_task_(process_cron_triggers_v2))
```

```python

cron_trigger_opts = [
    cfg.BoolOpt(
        'enabled',
        default=True,
        help=(
            'If this value is set to False then the subsystem of cron triggers'
            ' is disabled. Disabling cron triggers increases system'
            ' performance.'
        )
    ),
    cfg.IntOpt(
        'execution_interval',
        default=1,
        min=1,
        help=(
            'This setting defines how frequently Mistral checks for cron '
            'triggers that need execution. By default this is every second '
            'which can lead to high system load. Increasing the number will '
            'reduce the load but also limit the minimum freqency. For '
            'example, a cron trigger can be configured to run every second '
            'but if the execution_interval is set to 60, it will only run '
            'once per minute.'
        )
    )
]
```

Method `process_cron_triggers_v2` thực hiện:

lấy tất cả các job đến hạn cần thực hiện (next_execution_time< thời điểm hiện tại) và đặt message của job này vào queue để thực thi.

```python
def process_cron_triggers_v2(self, ctx):
    LOG.debug("Processing cron triggers...")

    for trigger in triggers.get_next_cron_triggers():
        LOG.debug("Processing cron trigger: %s", trigger)

        try:
             rpc.get_engine_client().start_workflow(
                    trigger.workflow.name,
                    trigger.workflow.namespace,
                    None,
                    trigger.workflow_input,
                    description=json.dumps(description),
                    **trigger.workflow_params
                )
        except Exception:
            # Log and continue to next cron trigger.
            LOG.exception(
                "Failed to process cron trigger %s",
                str(trigger)
            )
        finally:
            auth_ctx.set_ctx(None)
```

```python
def get_next_cron_triggers():
    return db_api.get_next_cron_triggers(
        datetime.datetime.utcnow() + datetime.timedelta(0, 2)
    )

@b.session_aware()
def get_next_cron_triggers(time, session=None):
    query = b.model_query(models.CronTrigger)

    query = query.filter(models.CronTrigger.next_execution_time < time)
    query = query.order_by(models.CronTrigger.next_execution_time)

    return query.all()


```

Sau đó method này gọi tới method croniter để lấy lần execution tiếp theo của một job được thực thi vào lần này và cập nhật vào database khi cần thiết.

```python
            next_time = triggers.get_next_execution_time(
                t.pattern,
                max(datetime.datetime.utcnow(), t.next_execution_time)
            )
```

```python
def get_next_execution_time(pattern, start_time):
    return croniter.croniter(pattern, start_time).get_next(
        datetime.datetime
    )

```

```python
def advance_cron_trigger(t):
    modified_count = 0

    try:
        # If the cron trigger is defined with limited execution count.
        if t.remaining_executions is not None and t.remaining_executions > 0:
            t.remaining_executions -= 1

        # If this is the last execution.
        if t.remaining_executions == 0:
            modified_count = triggers.delete_cron_trigger(
                t.name,
                trust_id=t.trust_id,
                delete_trust=False
            )
        else:  # if remaining execution = None or > 0.
            # In case the we are lagging or if the api stopped for some time
            # we use the max of the current time or the next scheduled time.
            next_time = triggers.get_next_execution_time(
                t.pattern,
                max(datetime.datetime.utcnow(), t.next_execution_time)
            )

            # Update the cron trigger with next execution details
            # only if it wasn't already updated by a different process.
            updated, modified_count = db_api_v2.update_cron_trigger(
                t.name,
                {
                    'next_execution_time': next_time,
                    'remaining_executions': t.remaining_executions
                },
                query_filter={
                    'next_execution_time': t.next_execution_time
                }
            )
    except exc.DBEntityNotFoundError as e:
        # Cron trigger was probably already deleted by a different process.
        LOG.debug(
            "Cron trigger named '%s' does not exist anymore: %s",
            t.name, str(e)
        )

    # Return True if this engine was able to modify the cron trigger in DB.
    return modified_count > 0
```

Job này thực hiện update next execution time của job khi cần
