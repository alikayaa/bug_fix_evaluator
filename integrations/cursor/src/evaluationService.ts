import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { execSync, spawn } from 'child_process';
import { promises as fsPromises } from 'fs';

export interface EvaluationParams {
  repoPath: string;
  engineerBeforeCommit: string;
  engineerAfterCommit: string;
  aiBeforeCommit: string;
  aiAfterCommit: string;
  outputFormat?: string;
}

export interface EvaluationResult {
  overall_score: number;
  scores: Record<string, number>;
  report_path: string;
  strengths: string[];
  weaknesses: string[];
}

export interface ReportInfo {
  name: string;
  date: string;
  path: string;
  score?: number;
}

export class EvaluationService {
  private context: vscode.ExtensionContext;
  private pythonPath: string | undefined;
  private outputDir: string | undefined;
  private reportPanel: vscode.WebviewPanel | undefined;

  constructor(context: vscode.ExtensionContext) {
    this.context = context;
    this.updateSettings();

    // Listen for configuration changes
    vscode.workspace.onDidChangeConfiguration(e => {
      if (e.affectsConfiguration('bugFixEvaluator')) {
        this.updateSettings();
      }
    });
  }

  private updateSettings(): void {
    const config = vscode.workspace.getConfiguration('bugFixEvaluator');
    this.pythonPath = config.get<string>('pythonPath') || this.findPythonPath();
    
    let outputDir = config.get<string>('outputDirectory') || '';
    // Replace workspace placeholder if present
    if (outputDir.includes('${workspaceFolder}') && vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
      const workspaceFolder = vscode.workspace.workspaceFolders[0].uri.fsPath;
      outputDir = outputDir.replace('${workspaceFolder}', workspaceFolder);
    }
    this.outputDir = outputDir;
  }

  private findPythonPath(): string {
    try {
      // Try to find python in the PATH
      const pythonCommand = process.platform === 'win32' ? 'where python' : 'which python3 || which python';
      const result = execSync(pythonCommand, { encoding: 'utf8' }).trim();
      return result.split('\n')[0]; // Take the first result
    } catch (error) {
      return ''; // Return empty string if python not found
    }
  }

  private generatePythonArgs(params: EvaluationParams): string[] {
    const args = [
      '-m', 'bug_fix_evaluator',
      '--repo-path', params.repoPath,
      '--engineer-before', params.engineerBeforeCommit,
      '--engineer-after', params.engineerAfterCommit,
      '--ai-before', params.aiBeforeCommit,
      '--ai-after', params.aiAfterCommit
    ];

    if (params.outputFormat) {
      args.push('--format', params.outputFormat);
    } else {
      args.push('--format', 'html');
    }

    if (this.outputDir) {
      args.push('--output-dir', this.outputDir);
    }

    return args;
  }

  public async evaluateFromCommits(params: EvaluationParams): Promise<EvaluationResult> {
    return new Promise<EvaluationResult>((resolve, reject) => {
      if (!this.pythonPath) {
        reject(new Error('Python path not configured. Please set the bugFixEvaluator.pythonPath setting.'));
        return;
      }

      const args = this.generatePythonArgs(params);
      
      let outputData = '';
      let errorData = '';

      const process = spawn(this.pythonPath, args);

      process.stdout.on('data', (data) => {
        outputData += data.toString();
      });

      process.stderr.on('data', (data) => {
        errorData += data.toString();
      });

      process.on('error', (error) => {
        reject(new Error(`Failed to run evaluation: ${error.message}`));
      });

      process.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Evaluation process exited with code ${code}: ${errorData}`));
          return;
        }

        try {
          // Extract the JSON result from stdout
          const resultMatch = outputData.match(/RESULT_JSON_START(.*)RESULT_JSON_END/s);
          if (!resultMatch) {
            reject(new Error('Could not parse evaluation result from output'));
            return;
          }

          const resultJson = resultMatch[1].trim();
          const result = JSON.parse(resultJson) as EvaluationResult;
          resolve(result);
        } catch (error) {
          reject(new Error(`Failed to parse evaluation result: ${(error as Error).message}`));
        }
      });
    });
  }

  public async getReports(): Promise<ReportInfo[]> {
    if (!this.outputDir || !fs.existsSync(this.outputDir)) {
      return [];
    }

    try {
      const files = await fsPromises.readdir(this.outputDir);
      const reportFiles = files.filter(f => 
        f.endsWith('.html') || f.endsWith('.json') || f.endsWith('.md') || f.endsWith('.txt')
      );

      const reports: ReportInfo[] = [];
      for (const file of reportFiles) {
        const filePath = path.join(this.outputDir, file);
        const stats = await fsPromises.stat(filePath);
        
        // Extract date from file name or use file modification date
        let dateString = stats.mtime.toISOString();
        const dateMatch = file.match(/\d{4}-\d{2}-\d{2}/);
        if (dateMatch) {
          dateString = dateMatch[0];
        }

        reports.push({
          name: file,
          date: dateString,
          path: filePath
        });
      }

      // Sort by most recent first
      return reports.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
    } catch (error) {
      console.error('Error getting reports:', error);
      return [];
    }
  }

  public async showReport(reportPath: string): Promise<void> {
    if (!fs.existsSync(reportPath)) {
      vscode.window.showErrorMessage(`Report file not found: ${reportPath}`);
      return;
    }

    // Determine report type from extension
    const ext = path.extname(reportPath).toLowerCase();
    
    if (ext === '.html') {
      // Show HTML report in WebView
      if (this.reportPanel) {
        this.reportPanel.dispose();
      }

      this.reportPanel = vscode.window.createWebviewPanel(
        'bugFixEvaluatorReport',
        `Report: ${path.basename(reportPath)}`,
        vscode.ViewColumn.One,
        { 
          enableScripts: true,
          retainContextWhenHidden: true
        }
      );

      const content = await fsPromises.readFile(reportPath, 'utf8');
      this.reportPanel.webview.html = content;

      // Handle panel close
      this.reportPanel.onDidDispose(() => {
        this.reportPanel = undefined;
      });
    } else {
      // For other file types, just open them in the editor
      const document = await vscode.workspace.openTextDocument(reportPath);
      await vscode.window.showTextDocument(document);
    }
  }
} 