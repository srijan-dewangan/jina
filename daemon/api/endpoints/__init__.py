from fastapi import APIRouter
from jina.logging.profile import used_memory_readable
from jina.helper import get_public_ip, get_internal_ip, get_full_version

from ...models import DaemonStatus
from ...stores import workspace_store, pea_store, pod_store, flow_store

router = APIRouter(tags=['daemon'])


@router.on_event('startup')
async def startup():
    """Start the process"""
    from ... import daemon_logger, jinad_args

    daemon_logger.info(
        f'''
Welcome to Jina daemon - the manager of distributed Jina
💬 Swagger UI     :\thttp://localhost:{jinad_args.port_expose}/docs
📚 Redoc          :\thttp://localhost:{jinad_args.port_expose}/redoc
🔒 Private address:\thttp://{get_internal_ip()}:{jinad_args.port_expose}
🌐 Public address :\thttp://{get_public_ip()}:{jinad_args.port_expose}'''
    )
    from jina import __ready_msg__

    daemon_logger.success(__ready_msg__)


@router.get(
    path='/',
)
async def _home():
    """
    The instruction HTML when user visits `/` directly


    .. #noqa: DAR201
    """
    return {}


@router.get(
    path='/status', summary='Get the status of the daemon', response_model=DaemonStatus
)
async def _status():
    _jina, _envs = get_full_version()
    return {
        'jina': _jina,
        'envs': _envs,
        'workspaces': workspace_store.status,
        'peas': pea_store.status,
        'pods': pod_store.status,
        'flows': flow_store.status,
        'used_memory': used_memory_readable(),
    }
