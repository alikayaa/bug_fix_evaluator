import * as vscode from 'vscode';
import { EvaluationProvider } from './evaluationProvider';
import { EvaluationService } from './evaluationService';
import { showInputDialog, showMessageWithOptions } from './ui';

export async function activate(context: vscode.ExtensionContext) {
  console.log('Bug Fix Evaluator extension is now active');

  // Create our services
  const evaluationService = new EvaluationService(context);
  
  // Register the tree view for showing evaluations
  const evaluationProvider = new EvaluationProvider(evaluationService);
  const evaluationView = vscode.window.createTreeView('bugFixEvaluatorExplorer', {
    treeDataProvider: evaluationProvider,
    showCollapseAll: true
  });
  
  // Register the evaluate command
  const evaluateCommand = vscode.commands.registerCommand('bug-fix-evaluator.evaluate', async () => {
    try {
      // Get repository information
      const workspaceFolders = vscode.workspace.workspaceFolders;
      if (!workspaceFolders || workspaceFolders.length === 0) {
        vscode.window.showErrorMessage('Please open a workspace with a git repository.');
        return;
      }
      
      const repoPath = workspaceFolders[0].uri.fsPath;
      
      // Collect information via input dialogs
      const engineerBeforeCommit = await showInputDialog(
        'Enter the commit SHA before the engineer\'s fix'
      );
      if (!engineerBeforeCommit) { return; }
      
      const engineerAfterCommit = await showInputDialog(
        'Enter the commit SHA after the engineer\'s fix'
      );
      if (!engineerAfterCommit) { return; }
      
      const aiBeforeCommit = await showInputDialog(
        'Enter the commit SHA before the AI\'s fix'
      );
      if (!aiBeforeCommit) { return; }
      
      const aiAfterCommit = await showInputDialog(
        'Enter the commit SHA after the AI\'s fix'
      );
      if (!aiAfterCommit) { return; }
      
      // Show progress indicator
      await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: 'Evaluating bug fixes...',
        cancellable: false
      }, async (progress) => {
        progress.report({ increment: 0 });
        
        try {
          // Run the evaluation
          const result = await evaluationService.evaluateFromCommits({
            repoPath,
            engineerBeforeCommit,
            engineerAfterCommit,
            aiBeforeCommit,
            aiAfterCommit
          });
          
          progress.report({ increment: 100 });
          
          // Show results summary
          const score = result.overall_score.toFixed(1);
          const message = `Evaluation complete! Overall score: ${score}%`;
          
          const choice = await showMessageWithOptions(
            message,
            { modal: false },
            { title: 'Show Report', isCloseAffordance: false },
            { title: 'OK', isCloseAffordance: true }
          );
          
          if (choice && choice.title === 'Show Report') {
            await vscode.commands.executeCommand('bug-fix-evaluator.showReport', result.report_path);
          }
          
          // Refresh the evaluations view
          evaluationProvider.refresh();
        } catch (error) {
          vscode.window.showErrorMessage(`Evaluation failed: ${error.message}`);
        }
      });
    } catch (error) {
      vscode.window.showErrorMessage(`Error during evaluation: ${error.message}`);
    }
  });
  
  // Register the show report command
  const showReportCommand = vscode.commands.registerCommand(
    'bug-fix-evaluator.showReport', 
    async (reportPath?: string) => {
      if (!reportPath) {
        const reports = await evaluationService.getReports();
        if (reports.length === 0) {
          vscode.window.showInformationMessage('No evaluation reports found.');
          return;
        }
        
        const items = reports.map(r => ({ 
          label: r.name, 
          description: r.date,
          path: r.path
        }));
        
        const selection = await vscode.window.showQuickPick(items, {
          placeHolder: 'Select a report to view'
        });
        
        if (!selection) { return; }
        reportPath = selection.path;
      }
      
      // Open the report in a webview
      await evaluationService.showReport(reportPath);
    }
  );
  
  // Register the configure command
  const configureCommand = vscode.commands.registerCommand('bug-fix-evaluator.configure', async () => {
    await vscode.commands.executeCommand('workbench.action.openSettings', 'bugFixEvaluator');
  });
  
  // Register our disposables
  context.subscriptions.push(
    evaluateCommand,
    showReportCommand,
    configureCommand,
    evaluationView
  );
}

export function deactivate() {
  // Clean up any resources if needed
} 