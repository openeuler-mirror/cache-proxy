import config


class ProxyManager:
    def __init__(self):
        self.open_proxy_rules = config.OPEN_PROXY_RULES
        self.proxy_rules = config.SUFFIX_RULES.split() if config.SUFFIX_RULES else []

    def rules_filter(self, url):
        for rule in self.proxy_rules:
            if url.endswith(rule):
                return True
        return False

    def always_access(self, url):
        return True

    def close_or_none(self):
        if not self.open_proxy_rules:
            return True
        if not self.proxy_rules:
            return True
