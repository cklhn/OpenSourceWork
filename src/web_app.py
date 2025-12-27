"""
Flask Web应用
"""
from flask import Flask, render_template, jsonify
from . storage import Database


def create_app(db_path: str = "data/analysis.db") -> Flask:
    app = Flask(__name__, template_folder='../templates')
    app.config['SECRET_KEY'] = 'dev-key'

    db = Database(db_path)

    @app.route('/')
    def index():
        projects = db.get_all_projects()
        return render_template('index.html', projects=projects)

    @app.route('/api/projects')
    def api_projects():
        return jsonify(db.get_all_projects())

    @app.route('/api/project/<int:pid>')
    def api_project(pid):
        project = db.get_project(pid)
        if not project:
            return jsonify({'error': '项目不存在'}), 404

        contributors = db.get_contributor_stats(pid)
        smells = db.get_code_smells(pid)
        files = db.get_file_stats(pid)
        commits = db.get_commits(pid, limit=20)

        return jsonify({
            'project': project,
            'contributors': contributors,
            'smells': smells,
            'files': files[: 20],  # 只返回前20个文件
            'recent_commits': commits
        })

    @app.route('/api/project/<int:pid>/contributors')
    def api_contributors(pid):
        return jsonify(db.get_contributor_stats(pid))

    @app.route('/api/project/<int:pid>/files')
    def api_files(pid):
        return jsonify(db.get_file_stats(pid))

    @app.route('/api/project/<int:pid>/commits')
    def api_commits(pid):
        return jsonify(db.get_commits(pid))

    return app
