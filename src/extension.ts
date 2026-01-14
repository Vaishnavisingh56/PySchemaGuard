// ─────────────────────────────────────────────────────────────
// SQL VALIDATOR VS CODE EXTENSION  (Live Runtime Tool - Level 3)
// ─────────────────────────────────────────────────────────────

import * as vscode from "vscode";
import { exec } from "child_process";

// ⚙️ IMPORTANT: Update these paths to match your system
const PROJECT_DIR = "C:\\Users\\hp\\sql-validator";
const PYTHON_PATH = "C:\\Users\\hp\\sql-validator\\env\\bin\\python.exe";

// ─────────────────────────────────────────────
// ACTIVATE EXTENSION
// ─────────────────────────────────────────────
export function activate(context: vscode.ExtensionContext) {
    console.log("🔌 SQL Validator Extension Activated");

    // 📌 Manual Command: Run From Command Palette
    const runCheck = vscode.commands.registerCommand("sql-validator.runCheck", () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) return vscode.window.showErrorMessage("No active file selected");

        const filePath = editor.document.fileName;
        const command = `${PYTHON_PATH} -m src.cli check "${filePath}" --json-output`;

        exec(command, { cwd: PROJECT_DIR }, (err, stdout, stderr) => {
            if (err || stderr) {
                const msg = stderr?.toString() || err?.message || "Unknown error";
                vscode.window.showErrorMessage("Validator Error: " + msg);
                return;
            }

            vscode.window.showInformationMessage("SQL Validation Complete ✔");
        });
    });

    context.subscriptions.push(runCheck);

    // ─────────────────────────────────────────────
    // LIVE VALIDATION ON TEXT CHANGE
    // ─────────────────────────────────────────────
    const diagnostics = vscode.languages.createDiagnosticCollection("sqlvalidator");
    context.subscriptions.push(diagnostics);

    vscode.workspace.onDidChangeTextDocument((event) => {
        const document = event.document;
        if (document.languageId !== "python") return; // only python files

        const filePath = document.fileName;
        const command = `${PYTHON_PATH} -m src.cli check "${filePath}" --json-output`;

        exec(command, { cwd: PROJECT_DIR }, (err, stdout, stderr) => {
            if (err || stderr) return; // if CLI crashes, skip to avoid freezing

            let diagList: vscode.Diagnostic[] = [];

            try {
                // cli.py MUST return: {"errors": [ ... ]}
                const json = JSON.parse(stdout);
                const results = json.errors || [];

                results.forEach((issue: any) => {
                    const lineIndex = issue.line - 1;
                    const lineText = document.lineAt(lineIndex).text;

                    // Try to locate the wrong column/table name
                    const wrongWord =
                        issue.suggestion ||
                        issue.message.split("'")[1] ||
                        lineText.trim();

                    const start = lineText.indexOf(wrongWord);
                    const end = start + wrongWord.length;

                    const range = new vscode.Range(lineIndex, start, lineIndex, end);

                    const diagnostic = new vscode.Diagnostic(
                        range,
                        `❌ ${issue.message}` +
                            (issue.suggestion ? `\n💡 Suggestion: ${issue.suggestion}` : ""),
                        vscode.DiagnosticSeverity.Error
                    );

                    diagList.push(diagnostic);
                });

            } catch {
                console.log("❗Live JSON parse failed → Output was not validator JSON");
            }

            diagnostics.set(document.uri, diagList);
        });
    });

    vscode.window.showInformationMessage("🟢 SQL Validator Live Mode Enabled (inline errors + tooltips)");
}

// ─────────────────────────────────────────────
// EXTENSION DEACTIVATION
// ─────────────────────────────────────────────
export function deactivate() {
    console.log("🔌 SQL Validator Extension Deactivated");
}
