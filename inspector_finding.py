import boto3
from deep_translator import GoogleTranslator
from github import Github
import os


PREVIOUS_RESULT_FILE = './vulnerability-list/vulnerability_list'

def main():
    # 前日分を取得
    vulnerability_list = get_revious_result_list()
    # 今日の分を取得
    critical_finding = get_critical_finding()
    print(str(len(critical_finding['findings'])) + ' critical findings found')

    issued_vulnerability = []
    for finding in critical_finding['findings']:
        # 前日データは除外
        if finding['packageVulnerabilityDetails']['vulnerabilityId'] not in vulnerability_list:
            instance_name = get_instance_name(finding['resources'])
            result = create_vulnerability_issue(f'{instance_name} - {finding["title"]}', translate(finding['description']),
                                                finding['description'], finding['packageVulnerabilityDetails']['sourceUrl'],
                                                get_instance_id_name(finding['resources']), '\n'.join(get_remediation(finding)))
            print(result)
            issued_vulnerability.append(finding['packageVulnerabilityDetails']['vulnerabilityId'])
    print(create_issued_vulnerability(issued_vulnerability))

def create_issued_vulnerability(vulnerability_list):
    # 差分を記録する
    # 差分があったら追記する
    if vulnerability_list == []:
        return "追加する脆弱性はありません"
    issued_vulnerability = '\n'.join(vulnerability_list)
    issued_vulnerability += '\n'
    # リストを改行区切りでファイルに追記する
    with open(PREVIOUS_RESULT_FILE, mode='a') as f:
        f.write(issued_vulnerability)
    return f"{','.join(vulnerability_list)}を追加しました"

def create_vulnerability_issue(title, trans_description, description, url, instace_name, remediation):
    # GitHubのリポジトリ名とトークンを環境変数から取得する
    repository_name = os.environ['GITHUB_REPOSITORY']
    token = os.environ['GH_TOKEN']
    g = Github(token)
    # イシューの本文を作成する
    body = f"""
    ### 説明
    {trans_description}
    ### 原文
    {description}
    ### 詳細
    {url}
    ### インスタンス名
    {instace_name}
    ### 対処方法
    ```bash
    {remediation}
    ```
    """
    # インデントを削除する
    body = body.replace("    ", "")
    repo = g.get_repo(repository_name)
    result = repo.create_issue(title=title, body=body)
    return result


def translate(text):
    return GoogleTranslator(source='auto', target='ja').translate(text)


def get_revious_result_list():
    # 前回の結果をリストで取得する
    vulnerability_list = []
    with open(PREVIOUS_RESULT_FILE) as f:
        for line in f:
            vulnerability_list.append(line.strip())
    return vulnerability_list


def get_instance_id_name(data):
    txt = ''
    for i in data:
        txt += i['tags']['Name'] + '(' + i['id'] + ')'
    return txt


def get_instance_name(data):
    txt = ''
    for i in data:
        txt += i['tags']['Name']
    return txt


def get_remediation(data):
    remediation = [i['remediation']
                   for i in data['packageVulnerabilityDetails']['vulnerablePackages']]
    return remediation


def get_critical_finding():
    inspector2 = boto3.client("inspector2")
    # ActiveかつCriticalの脆弱性を取得する
    critical_finding = inspector2.list_findings(filterCriteria={
        'findingStatus': [
            {
                'comparison': 'EQUALS',
                'value': 'ACTIVE'
            },
        ],
        'severity': [
            {
                'comparison': 'EQUALS',
                'value': 'CRITICAL'
            }
        ]
    }
    )
    return critical_finding

if __name__ == '__main__':
    main()