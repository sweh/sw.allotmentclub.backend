from .model import Object
import decimal
import re
import warnings

# VALUE_PER_MEMBER = 600000  # until end of 2015
# VALUE_PER_MEMBER = 750000  # until end of 2016
# VALUE_PER_MEMBER = 650000  # until end of 2018
VALUE_PER_MEMBER = 750000

SCAN_IGNORE_TESTS = [re.compile(r'\.testing$').search,
                     re.compile(r'\.conftest$').search,
                     re.compile(r'\.tests\.').search]

warnings.simplefilter('ignore')  # suppress sqlalchemy warnings


# Round for German expetations, e. g. 12.305 to 12.31:
decimal.DefaultContext.rounding = decimal.ROUND_HALF_UP


def json_result(data_list):
    """Remove meta information like `css_class` from result lists."""
    result = []
    for data in data_list:
        result.append([d['value'] for d in data])
    return result


# Initialize SQLAlchemy models
for module in ['model', 'user', 'bulletins', 'assignment', 'depot', 'protocol',
               'electricity', 'account', 'mail', 'keylist']:
    module = __import__(module, globals(), locals(), fromlist=None, level=1)
    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and issubclass(obj, Object):
            globals()[name] = obj
