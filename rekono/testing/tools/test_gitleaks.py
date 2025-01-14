from findings.models import Credential, Path
from targets.models import TargetEndpoint, TargetPort
from testing.tools.base import ToolParserTest
from tools.exceptions import ToolExecutionException


class GitLeaksParserTest(ToolParserTest):
    '''Test cases for GitLeaks parser.'''

    tool_name = 'GitLeaks'

    def test_check_installation(self) -> None:
        '''Test check installation feature for GitLeaks.'''
        installed = True
        try:
            self.tool.check_installation()
        except ToolExecutionException:
            installed = False
        self.assertFalse(installed)

    def test_leaky_repo(self) -> None:
        '''Test to parse report with secrets from https://github.com/Plazmaz/leaky-repo.'''
        expected = [
            {
                'model': Credential,
                'secret': 'token: "7f9cc25de23d1a255720b0ae4551f4044d600f46"',
                'context': '/.git/ : hub -> Line 4'
            },
            {'model': Credential, 'email': 'git@asdf.com', 'context': '/.git/ : Email of the commit author ASDF'},
            {'model': Credential, 'secret': 'xoxp-858723095049', 'context': '/.git/ : .bash_profile -> Line 23'},
            {
                'model': Credential,
                'secret': 'API_TOKEN=\'51e61afee2c2667123fc9ed160a0a20b330c8f74\'',
                'context': '/.git/ : .bash_profile -> Line 22'
            },
            {
                'model': Credential,
                'secret': 'API_KEY="38c47f19e349153fa963bb3b3212fe8e-us11"',
                'context': '/.git/ : .bashrc -> Line 106'
            },
            {
                'model': Credential,
                'secret': 'TOKEN=\"c77e01c1e89682e4d4b94a059a7fd2b37ab326ed\"',
                'context': '/.git/ : .bashrc -> Line 109'
            },
            {
                'model': Credential,
                'secret': '-----BEGIN RSA PRIVATE KEY-----',
                'context': '/.git/ : .ssh/id_rsa -> Line 1'
            },
            {
                'model': Credential,
                'secret': '-----BEGIN PRIVATE KEY-----',
                'context': '/.git/ : misc-keys/cert-key.pem -> Line 1'
            }
        ]
        self.tool.findings_relations = {                                        # Test with Path
            Path.__name__.lower(): Path.objects.create(path='/.git/', status=200)
        }
        super().check_tool_file_parser('leaky-repo.json', expected)
        target_port = TargetPort.objects.create(target=self.target, port=80)
        self.tool.findings_relations = {                                        # Test with TargetEndpoint
            TargetEndpoint.__name__.lower(): TargetEndpoint.objects.create(target_port=target_port, endpoint='/.git/')
        }
        self.tool.findings = []                                                 # Reset tool findings
        for item in expected:
            item['model'] = Credential                                          # Reset expected models
        super().check_tool_file_parser('leaky-repo.json', expected)
