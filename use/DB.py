import os, sqlite3
from Use import Use

class DB(object):

    def __init__(self, fn='.use.db'):
        self.filename = fn
        self._conn = sqlite3.connect(fn)
        self._conn.row_factory = sqlite3.Row
        self._init_db()
        self._buf = []
        self._keys = {}
        self._cur_key = 0

    def exists(self):
        return os.path.exists(self.filename)

    def key(self, obj):
        assert obj in self._keys
        return self._keys.get(obj)

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
            uses.append(Use(data))
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
            data['options'] = ("'%s'"%data['options']) if ('options' in data and data['options'] not in ({}, None)) else 'NULL'
            data['package'] = data['package'].replace("'", "''")
            str = '''INSERT OR REPLACE INTO uses(key, package, options)
                     VALUES('{key}', '{package}', {options});'''.format(**data)
            self._buf.append(str)

    def load_rules(self):

        # First load all rules.
        rule_map = {}
        cur = self._conn.cursor()
        cur.execute('SELECT * FROM rules')
        rules = []
        for data in cur:
            r = Rule(data)
            rule_map[data['key']] = r
            rules.append(r)

        # Next connect children.
        cur.execute('SELECT * FROM rules_children')
        for data in cur:
            r = rule_map[data['parent']]
            r.add_child(data['child'])

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
                              (parent INTEGER PRIMARY KEY, child INTEGER)''')
