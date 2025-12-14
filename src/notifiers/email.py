"""邮件通知模块"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime


class EmailNotifier:
    """邮件通知器"""

    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        use_tls: bool = True,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化邮件通知器

        Args:
            smtp_server: SMTP 服务器地址
            smtp_port: SMTP 端口
            username: 发件人邮箱
            password: 邮箱密码/应用专用密码
            use_tls: 是否使用 TLS
            logger: 日志记录器
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.logger = logger or logging.getLogger(__name__)

    def send(
        self,
        to_addresses: List[str],
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """
        发送邮件

        Args:
            to_addresses: 收件人列表
            subject: 邮件主题
            body: 邮件正文
            html: 是否为 HTML 格式

        Returns:
            是否发送成功
        """
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = ', '.join(to_addresses)
            msg['Subject'] = subject

            # 添加正文
            if html:
                msg.attach(MIMEText(body, 'html', 'utf-8'))
            else:
                msg.attach(MIMEText(body, 'plain', 'utf-8'))

            # 连接 SMTP 服务器
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)

            # 登录
            server.login(self.username, self.password)

            # 发送邮件
            server.send_message(msg)
            server.quit()

            self.logger.info(f"邮件发送成功: {subject}")
            return True

        except Exception as e:
            self.logger.error(f"邮件发送失败: {str(e)}", exc_info=True)
            return False

    def send_checkin_report(
        self,
        to_addresses: List[str],
        results: Dict[str, List[Dict[str, Any]]]
    ) -> bool:
        """
        发送签到报告

        Args:
            to_addresses: 收件人列表
            results: 签到结果字典 {站点名: [结果列表]}

        Returns:
            是否发送成功
        """
        # 统计
        total_success = 0
        total_failed = 0

        for site_results in results.values():
            for result in site_results:
                if result['success']:
                    total_success += 1
                else:
                    total_failed += 1

        # 构建 HTML 邮件
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #4CAF50; color: white; padding: 10px; }}
                .summary {{ margin: 20px 0; padding: 10px; background-color: #f0f0f0; }}
                .site {{ margin: 15px 0; }}
                .success {{ color: #4CAF50; }}
                .failed {{ color: #f44336; }}
                .result {{ margin: 5px 0; padding: 8px; border-left: 3px solid #ddd; }}
                .result.success {{ border-left-color: #4CAF50; }}
                .result.failed {{ border-left-color: #f44336; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>自动签到报告</h2>
            </div>

            <div class="summary">
                <strong>执行时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                <strong>总计:</strong>
                <span class="success">成功 {total_success}</span> /
                <span class="failed">失败 {total_failed}</span>
            </div>
        """

        # 添加每个站点的结果
        for site_name, site_results in results.items():
            html_body += f'<div class="site"><h3>{site_name.upper()}</h3>'

            for result in site_results:
                status_class = "success" if result['success'] else "failed"
                status_text = "✓ 成功" if result['success'] else "✗ 失败"

                html_body += f"""
                <div class="result {status_class}">
                    <strong>{result['username']}</strong> - {status_text}<br>
                    {result['message']}
                </div>
                """

            html_body += '</div>'

        html_body += """
        </body>
        </html>
        """

        # 发送邮件
        subject = f"签到报告 - {datetime.now().strftime('%Y-%m-%d')}"
        if total_failed > 0:
            subject += f" [有 {total_failed} 个失败]"

        return self.send(to_addresses, subject, html_body, html=True)
