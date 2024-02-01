import pytest
from producer.main import load_config, InvalidConfig


def test_missing_config():
    with pytest.raises(InvalidConfig):
        load_config('does-not-exist.yaml')


def test_invalid_content(tmp_path):
    content = '''
            %%%%%%%%%%\n
            number: 23\n
        '''

    tmp_conf = tmp_path / 'temp-config.yaml'
    tmp_conf.write_text(content)

    with pytest.raises(InvalidConfig):
        load_config(str(tmp_conf))


def test_valid_config(tmp_path):
    content = '''
        hello: yes\n
        number: 23\n
    '''

    tmp_conf = tmp_path / 'temp-config.yaml'
    tmp_conf.write_text(content)

    test_conf = load_config(str(tmp_conf))
    assert test_conf['hello'] is True
    assert test_conf['number'] == 23
