import os, sqlite3, json
from .Use import Use
from .Rule import Rule

class DB(object):

    DEFAULT_FILENAME='.use.db'

    def __init__(self, fn=DEFAULT_FILENAME):
        self.filename = fn if fn is not None else self.DEFAULT_FILENAME
        self._conn = sqlite3.connect(self.filename)
        self._conn.row_factory = sqlite3.Row
        self._init_db()
        self._buf = []
        self._keys = {}
        self._objs = {}
        self._cur_key = 0

    def exists(self):
        return os.path.exists(self.filename)

    def key(self, obj):
        assert obj in self._keys
        return self._keys.get(obj)

    def obj(self, key):
        assert key in self._objs
        return self._objs.get(key)

    def load_node(self, node):
        cur = self._conn.cursor()
        cur.execute("SELECT * FROM nodes WHERE key='%s'"%node.key)
        data = cur.fetchone()
        cur.close()
        node.load_data(data)

    def save_node(self, node):
        data = node.save_data()
        assert 'key' in data
        data['mtime'] = ("'%s'"%data['mtime'].strftime('%c')) if ('mtime' in data and data['mtime'] is not None) else 'NULL'
        data['crc'] = ("'%s'"%data['crc']) if ('crc' in data and data['crc'] is not None) else 'NULL'
        str = '''INSERT OR REPLACE INTO nodes(key, mtime, crc)
                  VALUES('{key}', {mtime}, {crc});'''.format(**data)
        self._buf.append(str)

    def load_uses(self):
        uses = []
        cur = self._conn.cursor()
        cur.execute('SELECT * FROM uses')
        for data in cur:
            key = data['key']
            data = {
                'package': data['package'],
                'installation': data['installation'] if 'installation' in data.keys() else None,
                'options': json.loads(data['options']) if 'options' in data.keys() else None
            }
            u = Use(data)
            uses.append(u)
            self._objs[key] = u
        cur.close()
        return uses

    def save_uses(self, uses):
        for use in uses:
            data = use.save_data()
            assert 'package' in data
            data['key'] = self._cur_key
            self._cur_key += 1
            assert use not in self._keys
            self._keys[use] = data['key']
            data['options'] = ("'%s'"%data['options']) if 'options' in data and data['options'] not in ({}, None) else 'NULL'
            data['package'] = data['package'].replace("'", "''")
            str = '''INSERT OR REPLACE INTO uses(key, package, options)
                     VALUES('{key}', '{package}', {options});'''.format(**data)
            self._buf.append(str)

    def load_rules(self):

        # First load all rules.
        cur = self._conn.cursor()
        cur.execute('SELECT * FROM rules')
        rules = []
        for data in cur:
            key = data['key']
            data = {
                'use': self.obj(data['use']),
                'options': json.loads(data['options']) if 'options' in data.keys() else None,
            }
            r = Rule(data)
            rules.append(r)
            self._objs[key] = r

        # Next connect children.
        cur.execute('SELECT * FROM rules_children')
        for data in cur:
            r = self.obj(data['parent'])
            r.add_children(self.obj(data['child']))

        return rules

    def save_rules(self, rules):

        # First pass for rules and data.
        for rule in rules:
            data = rule.save_data(self)
            assert 'use' in data
            data['key'] = self._cur_key
            self._cur_key += 1
            assert rule not in self._keys
            self._keys[rule] = data['key']
            data['options'] = ("'%s'"%data['options']) if ('options' in data and data['options'] not in ({}, None)) else 'NULL'
            str = '''INSERT OR REPLACE INTO rules(key, use, options)
                     VALUES('{key}', '{use}', {options});'''.format(**data)
            self._buf.append(str)

        # Second pass for children.
        for rule in rules:
            for child in rule.children:
                if isinstance(child, Rule):
                    data = {'parent': self.key(rule), 'child': self.key(child)}
                    str = '''INSERT INTO rules_children(parent, child)
                             VALUES('{parent}', '{child}');'''.format(**data)
                    self._buf.append(str)

    def save_arguments(self, args):
        data = args.save_data()
        for k, v in data.iteritems():
            v = json.dumps(v).replace("'", "''")
            str = '''INSERT OR REPLACE INTO arguments(key, value)
                     VALUES('%s', '%s');'''%(k, v)
            self._buf.append(str)

    def load_arguments(self, args):
        cur = self._conn.cursor()
        cur.execute('SELECT * FROM arguments')
        data = {}
        for entry in cur:
            data[entry['key']] = json.loads(entry['value'])
        args.load_data(data)

    def delete(self):
        # try:
        os.remove(self.filename)
        # except:
        #     pass

    def flush(self):
        if self._buf:
            cur = self._conn.cursor()
            for cmd in self._buf:
                cur.execute(cmd)
            self._conn.commit()
            cur.close()

    def _init_db(self):
        self._conn.execute('''CREATE TABLE IF NOT EXISTS nodes
                              (key TEXT PRIMARY KEY, mtime TEXT, crc TEXT)''')
        self._conn.execute('''CREATE TABLE IF NOT EXISTS uses
                              (key INTEGER PRIMARY KEY, package TEXT, options TEXT)''')
        self._conn.execute('''CREATE TABLE IF NOT EXISTS rules
                              (key INTEGER PRIMARY KEY, use INTEGER, options TEXT)''')
        self._conn.execute('''CREATE TABLE IF NOT EXISTS rules_children
                              (parent INTEGER, child INTEGER)''')
        self._conn.execute('''CREATE TABLE IF NOT EXISTS arguments
                              (key TEXT PRIMARY KEY, value TEXT)''')
