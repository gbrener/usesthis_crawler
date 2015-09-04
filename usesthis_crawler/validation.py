import urlparse
from usesthis_crawler import logger
from datetime import datetime


class ItemValidationError(Exception):
    def __init__(self, message, item=None):
        self.item = item


def is_valid_url(possible_url):
    comps = urlparse.urlparse(possible_url)
    return comps.scheme in ('http', 'https') and comps.netloc


def is_valid_src(possible_src):
    comps = urlparse.urlparse(possible_src)
    return comps.scheme in ('http', 'https') and comps.netloc and comps.path.endswith('.jpg')


def is_valid_date(possible_datestr):
    # This is necessary because datetime.strptime isn't strict about zero-padding
    if len(possible_datestr) != 10:
        return False
    try:
        datetime.strptime(possible_datestr, '%Y-%m-%d').date()
    except ValueError:
        return False
    return True


def missing_item_fields(item):
    return sorted(list(set(type(item).fields) - set(item)))


def validate_person_item(item, verbose=False):
    missing_fields = missing_item_fields(item)
    if missing_fields:
        raise ItemValidationError('PersonItem missing fields: {missing_fields}'.format(**locals()))

    name = item['name']
    article_url = item['article_url']
    if not name:
        err_msg = 'Interview at {article_url} doesn\'t have a person\'s name'.format(**locals())
        raise ItemValidationError(err_msg)

    if not is_valid_url(article_url):
        err_msg = '{name} ({article_url}) doesn\'t have a valid interview URL'.format(**locals())
        raise ItemValidationError(err_msg)

    pub_date = item['pub_date']
    if not is_valid_date(pub_date):
        err_msg = '{name} ({article_url}) doesn\'t have a publication date.'.format(**locals())
        raise ItemValidationError(err_msg)

    img_src = item['img_src']
    if not is_valid_src(img_src):
        err_msg = '{name} ({article_url}) doesn\'t have a valid image source URL ({img_src}).'.format(**locals())
        raise ItemValidationError(err_msg)

    if not item['bio']:
        logger.warn('%s (%s) doesn\'t have a bio.', name, article_url)

    if not item['hardware']:
        logger.warn('%s (%s) doesn\'t have a hardware section.', name, article_url)

    if not item['software']:
        logger.warn('%s (%s) doesn\'t have a software section.', name, article_url)

    if not item['dream']:
        logger.warn('%s (%s) doesn\'t have a dream-setup section.', name, article_url)


def is_valid_tool(tool, name, article_url, verbose):
    missing_fields = missing_item_fields(tool)
    if missing_fields:
        if verbose:
            logger.error('%s (%s) uses a tool that is missing fields %s. Skipping tool...', name, article_url, str(missing_fields))
        else:
            logger.error('Found tool (at %s) that is missing one or more fields. Skipping...', article_url)
        return False

    if not tool['tool_name']:
        if verbose:
            logger.error('%s (%s) uses a tool that doesn\'t have a name. Skipping tool...', name, article_url)
        else:
            logger.error('Found tool (at %s) that doesn\'t have a name. Skipping...', article_url)
        return False

    tool_name, tool_url = tool['tool_name'], tool['tool_url']
    if not is_valid_url(tool_url):
        if verbose:
            logger.error('%s (%s) uses a tool "%s" (%s) that doesn\'t have a valid URL. Skipping tool...', name, article_url, tool_name, tool_url)
        else:
            logger.error('Found tool (%s) that doesn\'t have a valid URL. Skipping...', tool_name)
        return False

    return True

    
def validate_tool_items(items, person_item, verbose=False):
    name = person_item['name']
    article_url = person_item['article_url']

    if not items:
        logger.warn('%s (%s) doesn\'t use any tools.', name, article_url)
        return

    # Replace the contents of `items` list with only the items that are valid
    items[:] = [item for item in items if is_valid_tool(item, name, article_url, verbose)]

    if not items:
        logger.warn('%s doesn\'t use any tools that have valid URLs.', name)
