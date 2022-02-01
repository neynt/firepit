import pandas as pd

import db
import lib

@lib.command()
def categories():
    return db.query_to_dataframe('''
    select * from categories order by name
    ''')

@lib.prompter('category_id')
def prompt_category(*_args):
    cats = categories()
    cat_names = cats.name.to_list()
    name = lib.prompt_list_nonstrict(cat_names, 'category: ')
    while True:
        if name in cat_names:
            return int(cats[cats.name == name].id)
        if lib.prompt_confirm(f'Create new category "{name}"?'):
            return lib.call_via_prompts(category_new, name)

def category_tree_lines():
    cats = db.query_to_dataframe('''
    select id, name, parent from categories c
    ''')
    roots = cats[pd.isna(cats.parent)].id
    def aux(id_, prefix):
        name = cats[cats.id == id_].name.iloc[0]
        yield (id_, prefix + name)
        children = cats[cats.parent == id_].id
        prefix = prefix[:-2] + ('│ ' if prefix[-2:] == '├ ' else '  ')
        for i, child_id in enumerate(children):
            last = i == len(children) - 1
            for line in aux(child_id, prefix + ('└ ' if last else '├ ')):
                yield line

    for i, root in enumerate(roots):
        last = i == len(roots) - 1
        for line in aux(root, '└ ' if last else '├ '):
            yield line

@lib.command()
def category_tree():
    for _category_id, line in category_tree_lines():
        print(line)

@lib.command(category='setup')
def category_new(name, parent_category_id=None):
    return db.insert('''
    insert into categories (name, parent) values (?, ?)
    ''', (name, parent_category_id))

@lib.command()
def category_del(category_id):
    db.execute('''
    delete from categories where id = ?
    ''', (category_id,))
