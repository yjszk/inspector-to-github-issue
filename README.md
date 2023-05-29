# Amazon Inspectorから脆弱性情報を取ってきてGitHub Issueに登録する

## 概要
- ACTIVEかつCRITICALの脆弱性情報を取得して、GitHub Issueに登録するPythonスクリプト
- GitHub Actionsで毎日JST10時ごろに実行するように設定している
- 記録済みの脆弱性はGitHub Artifactに保存している

## 絵

```mermaid
graph TD

A[GitHub Actionsでのスケジュール実行] --> Pythonでの処理

subgraph Pythonでの処理
  B[GitHub Artifactから前日分を取得]
  B --> C[新規分があるか?]
  C -- Yes --> D[Github Issueに脆弱性情報を登録]
  C -- No --> F[処理を終了]
end

D --> H[GitHub Artifactにアップロード]

```