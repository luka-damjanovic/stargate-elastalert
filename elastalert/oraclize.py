import os
import sys
import logging
import pickle

log = logging.getLogger('oraclize')


class OraclizeAlerts(object):
    """ This base class consists will be responsible for formatting any Oraclize
        specific alert messages before dispatching to any alert types.
        e.g.
            - converting data types to be more human readable
            - any extensive data comparison that cannot be achieved
              with the basic elastalert yaml config attributes
    """

    def __init__(self):
        self._cache = None
        self.MESSAGE_TYPE = { "DISK": self._format_disk_alert,
                              "CPU": self._format_cpu_alert,
                              "MEMORY": self._format_memory_alert
                            }

    def cached(cachefile):
        """
        A function that creates a decorator which will use "cachefile" for caching the
        results of the decorated function "fn".
        """
        def decorator(fn):
            def wrapped(self, *args, **kwargs):
                # if cache exists -> load it and return its content
                if os.path.exists(cachefile):
                        with open(cachefile, 'rb') as cachehandle:
                            print("using cached result from '%s'" % cachefile)
                            self._cache = pickle.load(cachehandle)

                # execute the function with all arguments passed
                res = fn(self, *args, **kwargs)

                # write to cache file
                with open(cachefile, 'wb') as cachehandle:
                    print("saving result to cache '%s'" % cachefile)
                    pickle.dump(self._cache, cachehandle)
                return res
            return wrapped
        return decorator

    def format_oraclize_alerts(self, alert_text_values, alert_arg_mapping):
        alert_text = unicode(self.rule.get('alert_text', ''))
        func = [func for substr, func in self.MESSAGE_TYPE.iteritems() if substr in alert_text]
        if len(func) > 0:
            log.info("Formatting alert <%s> with <%s>" % (alert_text, func[0]))
            return func[0](alert_text_values, alert_arg_mapping)

    @cached('/etc/elastalert/cache/disk_alert.obj')
    def _format_disk_alert(self, alert_text_values, alert_arg_mapping):
        _max = self.rule.get('max_threshold')
        try:
            val = self.match['system']['fsstat']['total_size']['used']
        except KeyError:
            return False
        if _max and val > _max:
            used = float(alert_arg_mapping['system.fsstat.total_size.used'])
            total = float(alert_arg_mapping['system.fsstat.total_size.total'])
            avg = (used / total) * 100
            cache_val = self._cache
            self._cache = int(avg)
            if int(avg) > cache_val:
                alert_text_values[0] = alert_arg_mapping['beat.hostname']
                alert_text_values[1] = '%.2f%%' % avg
                return alert_text_values
            else:
                return False

    @cached('/etc/elastalert/cache/cpu_alert.obj')
    def _format_cpu_alert(self, alert_text_values, alert_arg_mapping):
        _max = self.rule.get('max_threshold')
        try:
            val = self.match['system']['cpu']['total']['pct']
        except KeyError:
            return False
        if _max and val > _max:
            cpu_pct = '%.2f%%' % (alert_text_values[-1] * 100)
            cache_val = self._cache
            self._cache = int(val)
            if int(val) > cache_val:
                alert_text_values[-1] = cpu_pct
                return alert_text_values
            else:
                False

    @cached('/etc/elastalert/cache/memory_alert.obj')
    def _format_memory_alert(self, alert_text_values, alert_arg_mapping):
        _max = self.rule.get('max_threshold')
        try:
            val = self.match['system']['memory']['swap']['used']['pct']
        except KeyError:
            return False
        if _max and val > _max:
            cache_val = self._cache
            self._cache = int(val)
            if int(val) > cache_val:
                swap = float(alert_arg_mapping['system.memory.swap.used.pct']) * 100
                real = float(alert_arg_mapping['system.memory.actual.used.pct']) * 100
                alert_text_values[1:3] = '%.2f%%' % swap, '%.2f%%' % real
                return alert_text_values
            else:
                False
