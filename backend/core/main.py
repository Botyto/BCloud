from .context import BaseContext
from .data.context import SqlSettings, DataContext
from .app.main import AppContext, App

context = BaseContext()
sql_settings = SqlSettings("", 0, "", "", "")
context = DataContext.extend(context, sql=sql_settings)
context = AppContext.extend(context)
app = App(context)
app.run()
