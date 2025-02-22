# Norm

# What is Norm?

Norm claims that he is Not an Object Relational Mapping system. But he is in fact that. Or, at least, a very basic and work in progress-ish version of an ORM.

# Why use Norm?

## He’s classy

Norm gives you a Python class representation of a Shotgrid record instead of a dictionary.

```python
# The old way
shot['description']
>> 'HSM_SATL_0030'

# The Norm way
shot.description.get()
>> 'HSM_SATL_0030'
```

Instead of interacting directly with the api or the dictionaries you can use the class to get, set and delete data using the class.

This also means that we can have specific methods attached to entities. For example, if you'd like to create a bunch of time logs (you know those endless meetings?), you can do this:

```python
logs = TimeLog.repeating_log(description='A meeting',
                             start_date='2024-02-26',
                             start_time='10:30',
                             end_time='11:00',
                             project_id=7,
                             task_id=30,
                             repetitions=5)
```

You now have a `A meeting` entry for each day of the week.

## He knows you're lazy

Norm runs searches with less code and fetches all of the fields a record has without you needing to specify which fields you're interested in.

```python
# The old way
shot = sg.find_one('Shot', [['id', 'is', 123456]], ['description', 'sg_status_list'])

shot['description']
>> 'HSM_SATL_0030'

# The Norm way
shot = Shot.query.by_id(123456)
shot.description.get()
>> 'HSM_SATL_0030'
```

Here is a script that first finds a shot (we'll need some data from it) and then finds all the cameras attached to a project (we'll need their info as well)

```python
# Find our Shot in ShotGrid
filters = [
	['code', 'is', shot_name],
	['project', 'is', ctx.project]
]
fields = [
	'sg_lens', 'project', 'HB',
]

shot = tk.shotgun.find_one('Shot', filters, fields)

filters = [["project_sg_camera_projects", "is", ctx.project]]
fields = ['code', 'sg_plate_width', 'sg_plate_height', 'sg_sensor_width', 'sg_sensor_height']

cameras = tk.shotgun.find('CustomNonProjectEntity03', filters, fields)
```

And this is how Norm would do it:

```python
shot = Shot.query.filter_by(Shot().bingo == shot_name, Shot().project == ctx.project.get('id')).one()

cameras = shot.project.sg_camera
```

## He's a good navigator

### Navigating the old way

Let's say you wanted to get all of the tasks of a specific shot, in the old way you'd do something like:

```python
filters = [['entity', 'is', {'type': 'Shot', 'id': 29338}]]
fields = ['content']
results = sg.find('Task', filters, fields)
```

This gives us 5 task records with only the `content` field in it. But what if we also want some information from the shot? We need to revise our search

```python
filters = [['entity', 'is', {'type': 'Shot', 'id': 29338}]]
fields = ['content', 'entity.Shot.code']
results = sg.find('Task', filters, fields)
```

Want information about the users assigned to the task? Here's another search

```python
filters = [['entity', 'is', {'type': 'Shot', 'id': 29338}]]
fields = ['content', 'entity.Shot.code', 'task_assignees']
results = sg.find('Task', filters, fields)
```

But all you get for for the assigned people is this list of dictionaries:

```python
'task_assignees': [{'id': 577, 'name': 'Moshe Swed', 'type': 'HumanUser'}]
```

If you want anything more than the name of the user, say their department you'll now have to run a second search like this:

```python
filters = [['id', 'is', 577]]
fields = ['department.Department.name']
results = sg.find('HumanUser', filters, fields)
```

Notice that whenever we use dot notation to access related records we also have to know the name of the entity we're accessing, in this case we start with `Task` and then access `Shot`, `HumanUser` and `Department`

### Navigating Norm's way

The first thing to note is that Norm changes the orders of operations a bit, while we can search for the tasks directly it makes more sense to first find the shot.

```python
shot = Entity('Shot').query.by_id(29338).first()
```

To break it down, we create Shot entity class, run query based on the id, and return the first found record. In this case there is only one record, so it makes sense, but we can also use `.all()` to return a list of all found records

We can then simply access the tasks like this:

```python
tasks = shot.tasks
>>> [<TASK: anim>, <TASK: Caemra Track>, <TASK: fx>, <TASK: layout>, <TASK: lighting>]
```

Norm returns a list of Entity classes, one for each task. We can already see the `content` field as part of the class default return value, but if we want to operate on it we can do this:

```python
task = tasks[0]
task.bingo.get()
>>> 'anim'
```

Notice that we're using the `.bingo` property. This returns the name of an entity no matter what the name of the actual field is (it can be name, code, title, content and god knows what else). Also we did not need to know that the Entity type for tasks is called `Task`, Norm figured it out for us and returned the correct class.

We already have the shot, so getting the shot name is as simple as

```python
shot.bingo.get()
>>> 'HSM_SATL_0030'
```

Let's find out who's assigned to the task:

```python
user = task.task_assignees[0]
>>> [<HUMANUSER: Moshe Swed>]
```

And now get their department

```python
dept_name = user.department.bingo.get()
>>> '3D'
```

See? Norm searches for you behind the scenes and always returns classes which in turn can be used to search for more info.

## He goes both ways

Norm can do more than retrieve and display data, it can also be used to create new records or update existing ones.

Lets grab a task with a messed up name

```python
task = norm.Entity('Task').query.by_name('Something').first()
```

We can now fix the task name

```python
task.bingo.set('Camera Track')

task.bingo.get()
>>> 'Camera Track'
```

This changes the class property, but we still need to update shotgrid. To do that we use the Session class.

```python
norm.Session.current.add(task)  # We stage the change
norm.Session.current.commit()  # We commit the change
```

## Installation

```bash
pip install norm
```

## Development

### Clone the repository

```bash
git clone https://github.com/mswed/norm.git
```

### Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"
```
