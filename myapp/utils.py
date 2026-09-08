import bleach
from bleach.html5lib_shim import Filter
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


ALLOWED_BLOG_TAGS = ['link', 'script', 'div']


def _allowed_blog_attribute(tag: str, name: str, value: str) -> bool:
    if tag == 'link':
        return name == 'href' and value == 'https://actionnetwork.org/css/style-embed-v3.css'

    if tag == 'script':
        return (
            name == 'src'
            and value.startswith('https://actionnetwork.org/widgets/v6/petition/')
            and value.endswith('?format=js&source=widget')
        )

    return (
        tag == 'div'
        and (
            (name == 'id' and value == 'can-petition-area-support-hofstra-faculty')
            or (name == 'style' and value.strip() == 'width: 100%')
        )
    )


class _ActionNetworkScriptFilter(Filter):
    def __iter__(self):
        skip_script_end = False

        for token in self.source:
            if token['type'] == 'StartTag' and token['name'] == 'script':
                attributes = token.get('data', {})
                source = next(
                    (value for name, value in attributes.items() if name[-1] == 'src'),
                    None,
                )
                if source is None:
                    skip_script_end = True
                    continue

            if token['type'] == 'EndTag' and token['name'] == 'script':
                if skip_script_end:
                    skip_script_end = False
                    continue

            yield token


def sanitize_blog_body(body: str) -> str:
    cleaner = bleach.Cleaner(
        tags=ALLOWED_BLOG_TAGS,
        attributes=_allowed_blog_attribute,
        protocols=['https'],
        strip=True,
        filters=[_ActionNetworkScriptFilter],
    )
    return cleaner.clean(body)


def is_valid_email_format(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False
