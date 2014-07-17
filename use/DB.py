import os, sqlite3

class DB(object):

    def __init__(self, fn='.use.db'):
        self.filename = fn
        self._conn = sqlite3.connect(fn)
        self._conn.row_factory = sqlite3.Row
        self._init_db()
        self._buf = []
        self._keys = {}

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
            pass

    def load_rules(self):
        cur = self._conn.cursor()
        cur.execute('SELECT * FROM rules')
        rules = []
        for data in cur:
            r = Rule()
            r.load_data(data)
            rules.append(r)
        return rules

    def save_rules(self, rules):
        for rule in rules:
            data = rule.save_data()
            assert 'use' in data
            data['options'] = ("'%s'"%data['options']) if ('options' in data and data['options'] not in ({}, None)) else 'NULL'
            str = '''INSERT OR REPLACE INTO nodes(key, mtime, crc)
                     VALUES('{use}', {options});'''.format(**data)
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
                              (key INTEGER PRIMARY KEY, class TEXT, options TEXT)''')
        self._conn.execute('''CREATE TABLE IF NOT EXISTS rules
                              (key INTEGER PRIMARY KEY, use INTEGER, options TEXT)''')
        self._conn.execute('''CREATE TABLE IF NOT EXISTS rules_children
                              (parent INTEGER PRIMARY KEY, child INTEGER)''')
