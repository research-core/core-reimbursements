# CORE reimbursements module #

The module adds forms to submit reimbursements requests to the finance department.


## Installation & configuration

```python
pip install core-reimbursements
python manage.py migrate
```

To configure the logo in the print document and the next configuration to the settings.py file.

```python
REIMBURSEMENTS_LOGO = '...'
```


## The applications

The module adds the reimbursements option to the left menu.

![Menu](docs/images/menu.png)

Shows the list of reimbursements submitted by the users.

![Menu](docs/images/list.png)

Edit form.

![Menu](docs/images/edit-form.png)

Print version of the reimbursement.

![Menu](docs/images/print.png)