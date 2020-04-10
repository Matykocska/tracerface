from pytest import fixture
import unittest.mock as mock

from viewmodel.trace_setup import Setup
from viewmodel.viewmodel import ViewModel


@fixture
def nodes():
    return {
        'dummy_hash1': {
            'name': 'dummy_name1',
            'source': 'dummy_source1',
            'call_count': 0
        },
        'dummy_hash2': {
            'name': 'dummy_name2',
            'source': 'dummy_source2',
            'call_count': 1
        },
        'dummy_hash3': {
            'name': 'dummy_name3',
            'source': 'dummy_source1',
            'call_count': 2
        }
    }


@fixture
def edges():
    return {
        ('dummy_hash1', 'dummy_hash2'): {
            'params': [],
            'call_count': 0
        },
        ('dummy_hash1', 'dummy_hash3'): {
            'params': [['dummy_param']],
            'call_count': 3
        },
        ('dummy_hash2', 'dummy_hash3'): {
            'params': [['dummy_param1'], ['dummy_param2'], ['dummy_param3']],
            'call_count': 4
        }
    }


@mock.patch('viewmodel.viewmodel.BaseModel')
def test_viewmodel_initialization(model):
    setup = Setup()
    viewmodel = ViewModel(setup)

    assert viewmodel._model == model.return_value
    assert viewmodel._setup == setup


@mock.patch('viewmodel.viewmodel.BaseModel')
def test_get_nodes(model, nodes, edges):
    model.return_value.get_nodes.return_value = nodes
    setup = Setup()
    viewmodel = ViewModel(setup)

    assert viewmodel.get_nodes() == [
        {'data': {
            'count': 0,
            'id': 'dummy_hash1',
            'name': 'dummy_name1',
            'source': 'dummy_source1'
        }},
        {'data': {'count': 1,
            'id': 'dummy_hash2',
            'name': 'dummy_name2',
            'source': 'dummy_source2'
        }},
        {'data': {
            'count': 2,
            'id': 'dummy_hash3',
            'name': 'dummy_name3',
            'source': 'dummy_source1'
        }}
    ]


@mock.patch('viewmodel.viewmodel.BaseModel')
def test_get_edges(model, nodes, edges):
    model.return_value.get_nodes.return_value = nodes
    model.return_value.get_edges.return_value = edges
    setup = Setup()
    viewmodel = ViewModel(setup)

    assert viewmodel.get_edges() == [
        {'data': {
            'call_count': 0,
            'called_name': 'dummy_name2',
            'caller_name': 'dummy_name1',
            'params': '',
            'source': 'dummy_hash1',
            'target': 'dummy_hash2'
        }},
        {'data': {
            'call_count': 3,
            'called_name': 'dummy_name3',
            'caller_name': 'dummy_name1',
            'params': 'dummy_param',
            'source': 'dummy_hash1',
            'target': 'dummy_hash3'
        }},
        {'data': {
            'call_count': 4,
            'called_name': 'dummy_name3',
            'caller_name': 'dummy_name2',
            'params': '...',
            'source': 'dummy_hash2',
            'target': 'dummy_hash3'
        }}
    ]


@mock.patch('viewmodel.viewmodel.BaseModel')
def test_get_param_visuals(model, edges):
    model.return_value.get_edges.return_value = edges
    setup = Setup()
    viewmodel = ViewModel(setup)

    assert viewmodel.get_param_visuals_for_edge(('dummy_hash1', 'dummy_hash2')) == ''
    assert viewmodel.get_param_visuals_for_edge(('dummy_hash1', 'dummy_hash3')) == 'dummy_param'
    assert viewmodel.get_param_visuals_for_edge(('dummy_hash2', 'dummy_hash3')) == '...'


@mock.patch('viewmodel.viewmodel.BaseModel')
def test_get_params_of_edge(model, edges):
    model.return_value.get_edges.return_value = edges
    setup = Setup()
    viewmodel = ViewModel(setup)

    assert viewmodel.get_params_of_edge('dummy_hash1', 'dummy_hash2') == []
    assert viewmodel.get_params_of_edge('dummy_hash1', 'dummy_hash3') == [['dummy_param']]
    assert viewmodel.get_params_of_edge('dummy_hash2', 'dummy_hash3') == [
        ['dummy_param1'], ['dummy_param2'], ['dummy_param3']
    ]


@mock.patch('viewmodel.viewmodel.BaseModel')
def test_get_params_of_node(model, edges, nodes):
    model.return_value.get_nodes.return_value = nodes
    model.return_value.get_edges.return_value = edges
    setup = Setup()
    viewmodel = ViewModel(setup)

    assert viewmodel.get_params_of_node('dummy_hash2') == []
    assert viewmodel.get_params_of_node('dummy_hash3') == [
        ['dummy_param'], ['dummy_param1'], ['dummy_param2'], ['dummy_param3']
    ]


@mock.patch('viewmodel.viewmodel.BaseModel')
def test_color_counts_return_value_from_model(model):
    model.return_value.yellow_count.return_value = 4
    model.return_value.red_count.return_value = 4
    model.return_value.max_count.return_value = 4

    setup = Setup()
    viewmodel = ViewModel(setup)

    assert viewmodel.yellow_count() == 4
    assert viewmodel.red_count() == 4
    assert viewmodel.max_count() == 4


@mock.patch('viewmodel.viewmodel.StaticModel')
def test_output_submit_btn_clicked_uses_static_model(model):
    setup = Setup()
    viewmodel = ViewModel(setup)

    viewmodel.output_submit_btn_clicked('dummy text')

    assert viewmodel._model == model.return_value
    model.return_value.load_text.assert_called_once()
    model.return_value.load_text.assert_called_with('dummy text')


@mock.patch('viewmodel.viewmodel.DynamicModel')
def test_start_trace_uses_dynamic_model(model):
    setup = mock.Mock()
    setup.generate_bcc_args.return_value = 'dummy args'
    viewmodel = ViewModel(setup)

    viewmodel.start_trace()

    assert viewmodel._model == model.return_value
    model.return_value.start_trace.assert_called_once()
    model.return_value.start_trace.assert_called_with('dummy args')


@mock.patch('viewmodel.viewmodel.DynamicModel')
def test_stop_trace_uses_dynamic_model(model):
    setup = Setup()
    viewmodel = ViewModel(setup)
    viewmodel._model = model.return_value

    viewmodel.stop_trace()

    model.return_value.stop_trace.assert_called_once()


@mock.patch('viewmodel.viewmodel.BaseModel')
def test_set_range_uses_model(model):
    setup = Setup()
    viewmodel = ViewModel(setup)

    viewmodel.set_range('dummy', 'range')

    model.return_value.set_range.assert_called_once()
    model.return_value.set_range.assert_called_with('dummy', 'range')


@mock.patch('viewmodel.viewmodel.DynamicModel.thread_error', return_value='dummy_error')
@mock.patch('viewmodel.viewmodel.DynamicModel')
def test_thread_error_uses_model(model, error):
    setup = Setup()
    viewmodel = ViewModel(setup)
    viewmodel._model = model

    assert viewmodel.thread_error() == 'dummy_error'


@mock.patch('viewmodel.viewmodel.DynamicModel.process_error', return_value='dummy_error')
@mock.patch('viewmodel.viewmodel.DynamicModel')
def test_process_error_uses_model(model, error):
    setup = Setup()
    viewmodel = ViewModel(setup)
    viewmodel._model = model

    assert viewmodel.process_error() == 'dummy_error'


@mock.patch('viewmodel.viewmodel.DynamicModel.trace_active', return_value='dummy_status')
@mock.patch('viewmodel.viewmodel.DynamicModel')
def test_trace_active_uses_model(model, error):
    setup = Setup()
    viewmodel = ViewModel(setup)
    viewmodel._model = model

    assert viewmodel.trace_active() == 'dummy_status'


def test_add_app():
    setup = mock.Mock()
    viewmodel = ViewModel(setup)

    viewmodel.add_app(None)
    assert not setup.initialize_app.called

    viewmodel.add_app('app')
    setup.initialize_app.assert_called_with('app')


def test_remove_app():
    setup = mock.Mock()
    viewmodel = ViewModel(setup)

    viewmodel.remove_app(None)
    assert not setup.remove_app.called

    viewmodel.remove_app('app')
    setup.remove_app.assert_called_with('app')


def test_get_apps():
    setup = mock.Mock()
    setup.get_apps.return_value = 'dummy apps'
    viewmodel = ViewModel(setup)

    assert viewmodel.get_apps() == 'dummy apps'


def test_get_traced_functions_for_app():
    setup = mock.Mock()
    setup.get_setup_of_app.return_value = {
        'func1': {'traced': True},
        'func2': {'traced': False}
    }
    viewmodel = ViewModel(setup)

    assert viewmodel.get_traced_functions_for_app(None) == []
    assert viewmodel.get_traced_functions_for_app('dummy') == ['func1']


def test_get_not_traced_functions_for_app():
    setup = mock.Mock()
    setup.get_setup_of_app.return_value = {
        'func1': {'traced': True},
        'func2': {'traced': False}
    }
    viewmodel = ViewModel(setup)

    assert viewmodel.get_not_traced_functions_for_app(None) == []
    assert viewmodel.get_not_traced_functions_for_app('dummy') == ['func2']


def test_add_function():
    setup = mock.Mock()
    viewmodel = ViewModel(setup)

    viewmodel.add_function(None, None)
    viewmodel.add_function('app', None)
    viewmodel.add_function(None, 'func')
    assert not setup.add_function.called

    viewmodel.add_function('app', 'func')
    setup.add_function.assert_called_with('app', 'func')


def test_remove_function():
    setup = mock.Mock()
    viewmodel = ViewModel(setup)

    viewmodel.remove_function(None, None)
    viewmodel.remove_function('app', None)
    viewmodel.remove_function(None, 'func')
    assert not setup.remove_function.called

    viewmodel.remove_function('app', 'func')
    setup.remove_function.assert_called_with('app', 'func')


def test_get_parameters():
    setup = mock.Mock()
    setup.get_parameters.return_value = 'dummy params'
    viewmodel = ViewModel(setup)

    assert viewmodel.get_parameters(None, None) == {}
    assert viewmodel.get_parameters('app', 'func') == 'dummy params'


def test_add_parameter():
    setup = mock.Mock()
    viewmodel = ViewModel(setup)

    viewmodel.add_parameter(None, None, None, None)
    assert not setup.add_parameter.called

    viewmodel.add_parameter('app', 'func', '0', 'format')
    setup.add_parameter.assert_called_with('app', 'func', '0', 'format')


def test_remove_parameter():
    setup = mock.Mock()
    viewmodel = ViewModel(setup)

    viewmodel.remove_parameter(None, None, None)
    assert not setup.remove_parameter.called

    viewmodel.remove_parameter('app', 'func', '0')
    setup.remove_parameter.assert_called_with('app', 'func', 0)
