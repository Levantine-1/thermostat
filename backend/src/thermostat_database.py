import logging,  sqlite3, os
import config

# Setup logging
l = logging.getLogger(__name__)

# Global Vars
db_file = config.get['database']['db_file']

def configure_SQLite():
    try:
        l.info("Configuring SQLite3...")
        if os.path.exists(db_file):
            l.info("DB exists, resetting all values")
            db = sqlite3.connect(db_file)
            cur = db.cursor()
            cur.execute("UPDATE fan SET pk = '1', uuid = '' WHERE pk = '1'")
            cur.execute("UPDATE ac_scheduler SET pk = '1', uuid = '' WHERE pk = '1'")
            cur.execute("UPDATE ac_timer SET pk = '1', uuid = '' WHERE pk = '1'")
            db.commit()
            db.close()
        else:
            l.info("DB doesn't exist, creating tables...")
            db = sqlite3.connect("thermostat.db")
            cur = db.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS fan(pk, uuid)")
            cur.execute("CREATE TABLE IF NOT EXISTS ac_scheduler(pk, uuid)")
            cur.execute("CREATE TABLE IF NOT EXISTS ac_timer(pk, uuid)")
            cur.execute("INSERT INTO fan(pk, uuid) VALUES('1', '')")
            cur.execute("INSERT INTO ac_scheduler(pk, uuid) VALUES('1', '')")
            cur.execute("INSERT INTO ac_timer(pk, uuid) VALUES('1', '')")
            db.commit()
            db.close()
    except Exception:
        l.exception("Unable to setup database")
        raise


def query_db(task, table, data): # data could be empty string
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    if task == 'fetch':
        l.debug("Fetching data about table: " + table)
        query = cur.execute("SELECT uuid FROM " + table + " WHERE pk = '1'").fetchone()
        cur.close()
        db.close()
        l.debug("Result: " + str(query[0]))
        return query[0]
    elif task == 'update':
        l.info("Updating table: " + table + " with new uuid: " + str(data))
        cur.execute("UPDATE " + table + " SET uuid = '" + data + "' WHERE pk = '1'")
        updated_value = query_db(task='fetch', table=table, data='')
        db.commit()
        cur.close()
        db.close()
        l.info("Updated value: " + updated_value)
        return updated_value
