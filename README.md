# Amazon Inspectorから脆弱性情報を取ってきてGitHub Issueに登録する

## 概要
- ACTIVEかつCRITICALの脆弱性情報を取得して、GitHub Issueに登録するPythonスクリプト
- GitHub Actionsで毎日JST10時ごろに実行するように設定している
- 記録済みの脆弱性はGitHub Artifactに保存している

## 前提
- Amazon Inspectorの設定が完了していること
- 対象のGitHubのリポジトリから対象のAWSアカウントへの[認証が完了](https://docs.github.com/ja/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)していること

## 絵

```mermaid
graph TD

A[GitHub Actionsでのスケジュール実行] --> Pythonでの処理

subgraph Pythonでの処理
  B[GitHub Artifactから前日分を取得]
  B --> C[Amazon Inspectorから取得した新規分と前日分を突合]
  C -- 差分あり --> D[Github Issueに脆弱性情報を登録]
  C -- 差分なし --> F[処理を終了]
end

D --> H[GitHub Artifactにアップロード]

```
