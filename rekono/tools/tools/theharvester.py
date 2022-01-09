import json

from findings.enums import DataType
from findings.models import OSINT
from tools.tools.base_tool import BaseTool


class TheHarvesterTool(BaseTool):

    data_types = [
        ('ips', DataType.IP),
        ('hosts', DataType.DOMAIN),
        ('vhosts', DataType.DOMAIN),
        ('urls', DataType.URL),
        ('trello_urls', DataType.URL),
        ('emails', DataType.EMAIL),
        ('linkedin_links', DataType.LINK),
        ('asns', DataType.ASN),
        ('twitter_people', DataType.USER),
        ('linkedin_people', DataType.USER)
    ]

    def parse_output(self, output: str) -> None:
        with open(self.path_output) as output_file:
            data = json.load(output_file)
        for key, dt in self.data_types:
            if key in data:
                for item in data[key]:
                    self.create_finding(OSINT, data=item, data_type=dt)