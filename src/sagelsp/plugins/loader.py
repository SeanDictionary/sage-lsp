from collections.abc import Mapping, Sequence
from pluggy._hooks import HookImpl
from typing import Union
import logging
import pluggy

from sagelsp import NAME, hookspec

log = logging.getLogger(__name__)


class PluginManager(pluggy.PluginManager):
    def _hookexec(
        self,
        hook_name: str,
        methods: Sequence[HookImpl],
        kwargs: Mapping[str, object],
        firstresult: bool,
    ) -> Union[object, list[object]]:
        # called from all hookcaller instances.
        # enable_tracing will set its own wrapping function at self._inner_hookexec
        try:
            return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
        except Exception as e:
            log.warning(f"Failed to load hook {hook_name}: {e}", exc_info=True)
            return []

