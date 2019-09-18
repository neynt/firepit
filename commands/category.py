import pandas as pd

from prompt_toolkit import prompt

import db
import lib
import tabtab

@lib.command()
def categories():
    return db.query_to_dataframe('''
    select * from categories order by name
    ''')

def prompt_category():
    cats = categories()
    cat_names = cats.name.to_list()
    name = lib.prompt_list(cat_names, 'category')
    return int(cats[cats.name == name].id)

@lib.command()
def category_tree():
    cats = db.query_to_dataframe('''
    select c1.name as name, c2.name as parent
    from categories c1
    left join categories c2
    on c1.parent = c2.id
    ''')
    roots = cats[pd.isna(cats.parent)].name
    def aux(name, prefix):
        print(prefix + name)
        children = cats[cats.parent == name].name
        prefix = prefix[:-2] + ('│ ' if prefix[-2:] == '├ ' else '  ')
        for i, child in enumerate(children):
            last = i == len(children) - 1
            aux(child, prefix + ('└ ' if last else '├ '))

    for i, root in enumerate(roots):
        last = i == len(roots) - 1
        aux(root, '└ ' if last else '├ ')

@lib.command(category='setup')
def category_new(name, parent_category_id=None):
    db.execute('''
    insert into categories (name, parent) values (?, ?)
    ''', (name, parent_category_id))

@lib.command()
def category_del(category_id):
    db.execute('''
    delete from categories where id = ?
    ''', (category_id,))
