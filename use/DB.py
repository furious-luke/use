import os, sqlite3

class DB(object):

    def __init__(self, fn='.use.db'):
        self.filename = fn
        self._conn = sqlite3.connect(fn)
        self._conn.row_factory = sqlite3.Row
        self._init_db()
        self._buf = []

    def exists(self):
        return os.path.exists(fn)

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
                              (
