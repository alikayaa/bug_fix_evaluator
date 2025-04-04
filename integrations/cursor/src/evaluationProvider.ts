import * as vscode from 'vscode';
import * as path from 'path';
import { EvaluationService, ReportInfo } from './evaluationService';

export class EvaluationItem extends vscode.TreeItem {
  constructor(
    public readonly label: string,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState,
    public readonly reportInfo?: ReportInfo,
    public readonly tooltip?: string,
    public readonly iconPath?: string,
    public readonly command?: vscode.Command
  ) {
    super(label, collapsibleState);
    this.tooltip = tooltip;
    this.iconPath = iconPath;
    this.command = command;
  }
}

export class EvaluationProvider implements vscode.TreeDataProvider<EvaluationItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<EvaluationItem | undefined | null | void> =
    new vscode.EventEmitter<EvaluationItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<EvaluationItem | undefined | null | void> =
    this._onDidChangeTreeData.event;

  constructor(private evaluationService: EvaluationService) {}

  refresh(): void {
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: EvaluationItem): vscode.TreeItem {
    return element;
  }

  async getChildren(element?: EvaluationItem): Promise<EvaluationItem[]> {
    if (!element) {
      // Root level
      const reports = await this.evaluationService.getReports();
      if (reports.length === 0) {
        return [new EvaluationItem(
          'No evaluation reports found',
          vscode.TreeItemCollapsibleState.None,
          undefined,
          'Run an evaluation first to see results'
        )];
      }

      // Group reports by date
      const reportsByDate = new Map<string, ReportInfo[]>();
      for (const report of reports) {
        const date = report.date.split('T')[0]; // Get just the date part of ISO string
        if (!reportsByDate.has(date)) {
          reportsByDate.set(date, []);
        }
        reportsByDate.get(date)!.push(report);
      }

      // Create date group items
      const items: EvaluationItem[] = [];
      for (const [date, dateReports] of reportsByDate) {
        items.push(new EvaluationItem(
          date,
          vscode.TreeItemCollapsibleState.Collapsed,
          undefined,
          `${dateReports.length} report(s) from ${date}`
        ));
      }

      return items.sort((a, b) => b.label.localeCompare(a.label)); // Sort by date descending
    } else {
      // Reports for a specific date
      const reports = await this.evaluationService.getReports();
      const dateReports = reports.filter(r => r.date.startsWith(element.label));

      return dateReports.map(report => {
        const scoreDisplay = report.score !== undefined ? ` (${report.score.toFixed(1)}%)` : '';
        const label = `${path.basename(report.name, path.extname(report.name))}${scoreDisplay}`;
        
        return new EvaluationItem(
          label,
          vscode.TreeItemCollapsibleState.None,
          report,
          `${report.path}`,
          undefined,
          {
            command: 'bug-fix-evaluator.showReport',
            title: 'Open Report',
            arguments: [report.path]
          }
        );
      });
    }
  }
} 