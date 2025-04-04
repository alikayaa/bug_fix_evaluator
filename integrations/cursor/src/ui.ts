import * as vscode from 'vscode';

/**
 * Show an input dialog with the given prompt.
 * @param prompt The prompt to show in the dialog.
 * @param defaultValue The default value to pre-fill in the input box.
 * @returns The entered value, or undefined if the dialog was canceled.
 */
export async function showInputDialog(
  prompt: string,
  defaultValue: string = ''
): Promise<string | undefined> {
  return await vscode.window.showInputBox({
    prompt,
    value: defaultValue,
    ignoreFocusOut: true
  });
}

/**
 * Show a message with multiple options and return the selected option.
 * @param message The message to show.
 * @param options Modal options.
 * @param buttons One or more buttons to show.
 * @returns The selected button, or undefined if the message was dismissed.
 */
export async function showMessageWithOptions(
  message: string,
  options: vscode.MessageOptions,
  ...buttons: vscode.MessageItem[]
): Promise<vscode.MessageItem | undefined> {
  return await vscode.window.showInformationMessage(
    message,
    options,
    ...buttons
  );
}

/**
 * Show a quick pick selection from a list of items.
 * @param items The items to select from.
 * @param placeholder The placeholder text to show in the quick pick.
 * @returns The selected item, or undefined if the quick pick was dismissed.
 */
export async function showQuickPick<T extends vscode.QuickPickItem>(
  items: T[],
  placeholder: string
): Promise<T | undefined> {
  return await vscode.window.showQuickPick(items, {
    placeHolder: placeholder,
    ignoreFocusOut: true
  });
}

/**
 * Show a progress notification with the given title.
 * @param title The title to show in the progress notification.
 * @param task The task to run while showing the progress.
 * @returns The result of the task.
 */
export async function showProgress<T>(
  title: string,
  task: (progress: vscode.Progress<{ message?: string; increment?: number }>) => Promise<T>
): Promise<T> {
  return await vscode.window.withProgress(
    {
      location: vscode.ProgressLocation.Notification,
      title,
      cancellable: false
    },
    task
  );
} 