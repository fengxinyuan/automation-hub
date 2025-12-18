"""邮件通知模块"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime


def safe_quit(server: smtplib.SMTP) -> None:
    """
    QQ SMTP 在 QUIT 阶段偶尔会返回非 SMTP 文本数据（例如 b'\\x00\\x00\\x00'），
    smtplib 会因此抛 SMTPResponseException。
    发送已成功（queued）时，这类异常可以安全忽略。
    """
    try:
        server.quit()
    except smtplib.SMTPResponseException as e:
        # 常见：(-1, b'\x00\x00\x00')，忽略即可
        print(f"[提示] 忽略 QUIT 阶段异常：{e}")
        try:
            server.close()
        except Exception:
            pass
    except Exception as e:
        print(f"[提示] 退出阶段异常，直接关闭连接：{type(e).__name__}: {e}")
        try:
            server.close()
        except Exception:
            pass


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
        # 创建邮件
        msg = EmailMessage()
        msg['From'] = self.username
        msg['To'] = ', '.join(to_addresses)
        msg['Subject'] = subject

        # 添加正文
        if html:
            msg.set_content(body)
            msg.add_alternative(body, subtype='html')
        else:
            msg.set_content(body)

        # 优先尝试 SSL(465)，失败后尝试 STARTTLS(587)
        # 这是根据 test.py 成功测试的方法
        if self.smtp_port == 465:
            # 先尝试 SSL
            if self._send_with_ssl(msg, subject):
                return True
            # SSL 失败，尝试 STARTTLS
            self.logger.warning("SSL(465) 发送失败，尝试 STARTTLS(587)")
            return self._send_with_starttls(msg, subject)
        elif self.smtp_port == 587:
            # 直接使用 STARTTLS
            return self._send_with_starttls(msg, subject)
        else:
            # 对于其他端口，尝试两种方式
            if self._send_with_ssl(msg, subject):
                return True
            return self._send_with_starttls(msg, subject)

    def _send_with_ssl(self, msg: EmailMessage, subject: str) -> bool:
        """使用 SSL(465) 发送邮件"""
        server = None
        try:
            ctx = ssl.create_default_context()
            server = smtplib.SMTP_SSL(
                self.smtp_server, 465, timeout=30, context=ctx
            )
            server.ehlo_or_helo_if_needed()
            server.login(self.username, self.password)
            server.send_message(msg)
            self.logger.info(f"邮件发送成功 [SSL(465)]: {subject}")
            return True
        except Exception as e:
            self.logger.debug(f"SSL(465) 发送失败: {str(e)}")
            return False
        finally:
            if server is not None:
                safe_quit(server)

    def _send_with_starttls(self, msg: EmailMessage, subject: str) -> bool:
        """使用 STARTTLS(587) 发送邮件"""
        server = None
        try:
            ctx = ssl.create_default_context()
            server = smtplib.SMTP(self.smtp_server, 587, timeout=30)
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(self.username, self.password)
            server.send_message(msg)
            self.logger.info(f"邮件发送成功 [STARTTLS(587)]: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"STARTTLS(587) 发送失败: {str(e)}")
            return False
        finally:
            if server is not None:
                safe_quit(server)

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
                """

                # 如果是 Linux.do，添加帖子摘要
                if site_name == 'linuxdo' and result.get('details') and result['success']:
                    details = result['details']

                    # AI 推荐 - 最感兴趣的话题（优先显示）
                    if details.get('recommended_topics'):
                        html_body += '<h3 style="margin-top: 20px; color: #4CAF50;">🎯 AI 为你推荐 - 最可能感兴趣的话题</h3>'
                        for topic in details['recommended_topics'][:5]:
                            score = topic.get('relevance_score', 0)
                            reason = topic.get('recommendation_reason', '')
                            tags = topic.get('recommendation_tags', [])

                            html_body += f"""
                            <div style="margin: 15px 0; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        border-radius: 8px; color: white;">
                                <h4 style="margin: 0 0 10px 0; color: white;">
                                    <a href="https://linux.do{topic['link']}" target="_blank"
                                       style="color: white; text-decoration: none;">{topic['title']}</a>
                                </h4>
                                <div style="margin: 8px 0; font-size: 14px; opacity: 0.9;">
                                    📊 相关度: <strong>{score}%</strong> |
                                    👤 {topic['author']} |
                                    📁 {topic['category']} |
                                    💬 {topic['replies']} |
                                    👁️ {topic['views']}
                                </div>
                                <div style="margin: 8px 0; padding: 10px; background: rgba(255,255,255,0.1);
                                           border-radius: 4px; font-size: 14px;">
                                    📝 <strong>推荐理由:</strong> {reason}
                                </div>
                                {f'<div style="margin: 8px 0; font-size: 13px;">🏷️ {", ".join(tags)}</div>' if tags else ''}
                            </div>
                            """

                    # AI 深度分析
                    if details.get('ai_summaries'):
                        html_body += '<h3 style="margin-top: 20px;">🤖 AI 深度分析</h3>'
                        for topic in details['ai_summaries']:
                            ai_summary = topic.get('ai_summary', {})

                            html_body += f"""
                            <div style="margin: 15px 0; padding: 15px; background-color: #f0f8ff;
                                        border-left: 4px solid #2196F3; border-radius: 4px;">
                                <h4 style="margin: 0 0 10px 0;">
                                    <a href="https://linux.do{topic['link']}" target="_blank">{topic['title']}</a>
                                </h4>
                                <div style="margin: 5px 0; color: #666; font-size: 13px;">
                                    👤 {topic['author']} | 📁 {topic['category']}
                                </div>
                            """

                            # AI 摘要
                            if ai_summary.get('summary'):
                                html_body += f"""
                                <div style="margin: 10px 0; padding: 10px; background: white; border-radius: 4px;">
                                    <strong>📝 AI 摘要:</strong><br>
                                    <em style="color: #555;">{ai_summary['summary']}</em>
                                </div>
                                """

                            # 关键要点
                            if ai_summary.get('key_points'):
                                html_body += '<div style="margin: 10px 0;"><strong>🔑 关键要点:</strong><ul style="margin: 5px 0;">'
                                for point in ai_summary['key_points'][:3]:
                                    html_body += f'<li style="color: #555;">{point}</li>'
                                html_body += '</ul></div>'

                            # 标签和情感
                            if ai_summary.get('tags') or ai_summary.get('sentiment'):
                                html_body += '<div style="margin: 10px 0; font-size: 13px;">'
                                if ai_summary.get('tags'):
                                    html_body += f'🏷️ {", ".join(ai_summary["tags"])} &nbsp;&nbsp;'
                                if ai_summary.get('sentiment'):
                                    sentiment = ai_summary['sentiment']
                                    sentiment_emoji = {"positive": "😊", "negative": "😟", "neutral": "😐"}
                                    html_body += f'💭 {sentiment_emoji.get(sentiment, "😐")} {sentiment}'
                                html_body += '</div>'

                            html_body += '</div>'

                    # 最新帖子
                    if details.get('latest_topics'):
                        html_body += '<h4 style="margin-top: 20px;">📰 最新帖子</h4><ul>'
                        for topic in details['latest_topics'][:10]:
                            html_body += f"""
                            <li style="margin: 8px 0;">
                                <a href="https://linux.do{topic['link']}" target="_blank">{topic['title']}</a><br>
                                <small style="color: #666;">
                                    👤 {topic['author']} |
                                    📁 {topic['category']} |
                                    💬 {topic['replies']} |
                                    👁️ {topic['views']}
                                </small>
                            </li>
                            """
                        html_body += '</ul>'

                    # 热门话题
                    if details.get('hot_topics'):
                        html_body += '<h4 style="margin-top: 20px;">🔥 热门话题</h4><ul>'
                        for topic in details['hot_topics'][:10]:
                            html_body += f"""
                            <li style="margin: 8px 0;">
                                <a href="https://linux.do{topic['link']}" target="_blank">{topic['title']}</a><br>
                                <small style="color: #666;">
                                    👤 {topic['author']} |
                                    📁 {topic['category']} |
                                    💬 {topic['replies']} |
                                    👁️ {topic['views']}
                                </small>
                            </li>
                            """
                        html_body += '</ul>'

                html_body += '</div>'

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
