# Slackの設定方法

## Slack Botの作成 & トークン取得

1. [Slack API](https://api.slack.com/apps)にアクセスし, `Create New App`をクリックします.

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/1.png" width="600">
</div>

2. `From scratch`を選択し, アプリ名とワークスペースを入力して`Create App`をクリックします. (アプリ名の例: `ImInbot`)

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/2-1.png" width="600">
</div>

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/2-2.png" width="600">
</div>

3. 作成した`App`の設定ページに移動します.

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/3.png" width="600">
</div>

4. 左側のメニューから`OAuth & Permissions`を選択します.

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/4.png" width="600">
</div>

5. 下の方にスクロールしたら出てくる`Scopes`セクションで, `Bot Token Scopes`に以下の権限を追加します:
   - `files:read`
   - `canvases:write`

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/5-1.png" width="600">
</div>

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/5-2.png" width="600">
</div>

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/5-3.png" width="600">
</div>

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/5-4.png" width="600">
</div>

6. ページ上部の`Install to Workspace`ボタンをクリックし, ワークスペースにアプリをインストールします.

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/6-1.png" width="600">
</div>

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/6-2.png" width="600">
</div>

7. インストールが完了後, `OAuth & Permissions`ページに戻り, `Bot User OAuth Token`を後で使用しますので, 記録しておいてください. (`xoxb-`で始まるトークン)

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Creation/7.png" width="600">
</div>

## Slack Botの招待
1. Slackアプリを開き, Slack Botをインストールしたワークスペースの任意のチャンネルに移動します.
メッセージに以下のコマンドを送信してBotを招待します:
   `/invite @YourAppName` (例: `/invite @ImInbot`)

<div align="center">
  <img src="./assets/SLACK_SETUP/Slack-Bot-Invitation/1.png" width="600">
</div>