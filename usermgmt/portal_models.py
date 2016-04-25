from django.db import connections

import functools


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class DbStudyGroup:
    """Representation of a group in the portal database"""

    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return 'DbStudyGroup({})'.format(repr(self.name))

    def __repr__(self):
        return str(self)


class DaoStudyGroup:
    """Helper for getting group-related information from the portal
    """

    @classmethod
    def all_groups(klass):
        result = []
        cursor = connections['cbioportal'].cursor()
        cursor.execute('SELECT groups FROM cancer_study')
        for res in dictfetchall(cursor):
            for group in res['groups'].split(';'):
                result.append(DbStudyGroup(group.strip()))
        return set(result)

    @classmethod
    def num_groups(klass):
        return len(klass.all_groups())

    @classmethod
    def exists(klass, name):
        return DbStudyGroup(name) in klass.all_groups()

    @classmethod
    def get(klass, name):
        assert klass.exists(name)
        return DbStudyGroup(name)


class DbUser:
    """Represents a user in the database"""

    def __init__(self, email, name, enabled):
        #: Email of user, identifier
        self.email = email
        #: Name of the user
        self.name = name
        #: Whether or not the user is enabled
        self.enabled = bool(enabled)

    def to_dict(self):
        return {
            'email': self.email,
            'name': self.name,
            'enabled': self.enabled,
        }

    def __eq__(self, other):
        return self.email == other.email

    def __lt__(self, other):
        return self.email < other.email

    def __hash__(self):
        return hash(self.email)

    def __str__(self):
        return 'DbUser({}, {}, {})'.format(list(map(
            repr, [self.name, self.email, self.enabled])))


class DaoUser:
    """Helper for getting user-related information from the portal
    """

    @classmethod
    def all_users(klass):
        result = []
        cursor = connections['cbioportal'].cursor()
        cursor.execute('SELECT email, name, enabled FROM users ORDER BY email')
        for res in dictfetchall(cursor):
            result.append(DbUser(res['email'], res['name'], res['enabled']))
        return result

    @classmethod
    def with_direct_access_to(klass, identifier):
        """Return DbUser objects with direct access to authority"""
        result = []
        val = 'cbioportal:' + identifier.upper()
        cursor = connections['cbioportal'].cursor()
        cursor.execute("""
            SELECT DISTINCT users.email, name, enabled
            FROM users
            INNER JOIN authorities
            ON authorities.email = users.email
            WHERE authorities.authority = %s
            ORDER BY email""", [val])
        for res in dictfetchall(cursor):
            result.append(DbUser(res['email'], res['name'], res['enabled']))
        return result

    @classmethod
    def user_exists(klass, email):
        cursor = connections['cbioportal'].cursor()
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = %s', [email])
        return cursor.fetchone()[0]

    @classmethod
    def num_users(klass):
        cursor = connections['cbioportal'].cursor()
        cursor.execute('SELECT COUNT(*) FROM users');
        return cursor.fetchone()[0]

    @classmethod
    def create_user(klass, email, name, enabled):
        cursor = connections['cbioportal'].cursor()
        cursor.execute('INSERT INTO users (email, name, enabled) VALUES (%s, %s, %s)',
                       [email, name, int(enabled)])

    @classmethod
    def update_user(klass, email, name, enabled):
        cursor = connections['cbioportal'].cursor()
        cursor.execute('UPDATE users SET name = %s, enabled = %s WHERE email = %s',
                       [name, int(enabled), email])

    @classmethod
    def delete_user(klass, email):
        cursor = connections['cbioportal'].cursor()
        cursor.execute('DELETE FROM users WHERE email = %s', [email])

    @classmethod
    def get_user(klass, email):
        cursor = connections['cbioportal'].cursor()
        cursor.execute('SELECT email, name, enabled FROM users WHERE email = %s', [email]);
        res = dictfetchall(cursor)
        if len(res) != 1:
            raise Exception('No such user found!')
        res = res[0]
        return DbUser(res['email'], res['name'], res['enabled'])


class DbStudy:
    """Representation of a study in the portal (read-only)"""
    
    def __init__(self, identifier, name, groups):
        #: Unique identifier, upper case is used in authorities table
        self.identifier = identifier
        #: Title of the study, for clearer identification only
        self.name = name
        #: ``set`` of the groups that the study is in
        self.groups = list(sorted(groups))

    def __eq__(self, other):
        return self.identifier == other.identifier

    def __lt__(self, other):
        return self.identifier < other.identifier

    def __hash__(self):
        return hash(self.identifier)

    def __str__(self):
        return 'DbStudy({}, {}, {})'.format(list(map(
            repr, [self.identifier, self.name, self.groups])))


class DaoStudy:
    """Helper for getting study-related information from the portal
    """

    @classmethod
    def all_studies(self):
        result = []
        cursor = connections['cbioportal'].cursor()
        cursor.execute(r"""
            SELECT cancer_study_identifier, name, groups
            FROM cancer_study
            ORDER BY cancer_study_identifier""")
        for res in dictfetchall(cursor):
            result.append(DbStudy(res['cancer_study_identifier'],
                                  res['name'],
                                  res['groups'].split(';')))
        return result

    @classmethod
    def get(self, identifier):
        result = []
        cursor = connections['cbioportal'].cursor()
        cursor.execute(r"""
            SELECT cancer_study_identifier, name, groups
            FROM cancer_study
            WHERE cancer_study_identifier = %s
            ORDER BY cancer_study_identifier""", [identifier])
        for res in dictfetchall(cursor):
            return DbStudy(res['cancer_study_identifier'],
                           res['name'],
                           res['groups'].split(';'))
        return result

    @classmethod
    def num_studies(self):
        cursor = connections['cbioportal'].cursor()
        cursor.execute('SELECT COUNT(*) FROM cancer_study');
        return cursor.fetchone()[0]

    @classmethod
    def exists(self, identifier):
        cursor = connections['cbioportal'].cursor()
        cursor.execute(r"""
            SELECT COUNT(*)
            FROM cancer_study
            WHERE UPPER(cancer_study_identifier) = UPPER(%s)
            """, [identifier]);
        return cursor.fetchone()[0] > 0


class DbAuthority:
    """Represents the access to a study or a group"""
    
    def __init__(self, authority, email):
        self.authority = authority
        if self.authority.startswith('cbioportal:'):
            self.authority = self.authority[len('cbioportal:'):]
        self.email = email

    @property
    @functools.lru_cache()
    def is_for_study(self):
        """Return True if authority is for a study"""
        return DaoStudy.exists(self.authority)


    def __eq__(self, other):
        return (self.authority == other.authority and
                self.email == other.email)

    def __lt__(self, other):
        return (self.authority < other.authority or
                (self.authority == other.authority and
                 self.email == other.email))

    def __hash__(self):
        return hash(self.authority) ^ hash(self.email)

    def __str__(self):
        return 'DbAuthority({}, {})'.format(list(map(
            repr, [self.authority, self.email])))


class DaoAuthority:
    """Helper for accessing DbAuthority objects"""

    @classmethod
    def update_authorities_for_user(klass, email, authorities):
        # Remove old authorities
        cursor = connections['cbioportal'].cursor()
        cursor.execute(r"""
            DELETE FROM authorities
            WHERE email = %s""", [email])
        # Add new authorities
        for authority in authorities:
            cursor.execute(r"""
                INSERT INTO authorities (email, authority)
                VALUE (%s, %s)""",
                [email, 'cbioportal:' + authority.upper()])

    @classmethod
    def update_authorities_for_study(klass, identifier, emails):
        # Remove old authorities
        cursor = connections['cbioportal'].cursor()
        cursor.execute(r"""
            DELETE FROM authorities
            WHERE authority = %s
            """, ['cbioportal:' + identifier.upper()])
        # Add new authorities
        for email in emails:
            cursor.execute(r"""
                INSERT INTO authorities (email, authority)
                VALUE (%s, %s)""",
                [email, 'cbioportal:' + identifier.upper()])

    @classmethod
    def update_authorities_for_group(klass, name, emails):
        klass.update_authorities_for_study(name, emails)

    @classmethod
    def for_user(klass, email):
        """Return DbAuthority objects for a given user"""
        result = []
        cursor = connections['cbioportal'].cursor()
        cursor.execute(r"""
            SELECT authority, email
            FROM authorities
            WHERE email = %s
            ORDER BY authority""", [email])
        for res in dictfetchall(cursor):
            result.append(DbAuthority(res['authority'], res['email']))
        return result
