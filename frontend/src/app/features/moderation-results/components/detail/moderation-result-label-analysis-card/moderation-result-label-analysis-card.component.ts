import { Component, input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatTreeModule } from '@angular/material/tree';
import { ModerationResultDetailCardShellComponent } from '../moderation-result-detail-card-shell/moderation-result-detail-card-shell.component';
import type { ModerationResultItem } from '../../../models/moderation-results.model';

interface ModerationLabelTreeNode {
  name: string;
  confidence: number | null;
  parentName: string | null;
  children: ModerationLabelTreeNode[];
}

@Component({
  selector: 'app-moderation-result-label-analysis-card',
  imports: [MatIconModule, MatTreeModule, ModerationResultDetailCardShellComponent],
  templateUrl: './moderation-result-label-analysis-card.component.html',
  styleUrl: './moderation-result-label-analysis-card.component.scss',
})
export class ModerationResultLabelAnalysisCardComponent {
  readonly item = input.required<ModerationResultItem>();

  readonly moderationLabelChildrenAccessor = (node: ModerationLabelTreeNode) => node.children;

  protected buildModerationLabelTree(item: ModerationResultItem): ModerationLabelTreeNode[] {
    const nodesByName = new Map<string, ModerationLabelTreeNode>();

    for (const label of item.moderation_labels) {
      nodesByName.set(label.Name, {
        name: label.Name,
        confidence: label.Confidence,
        parentName: label.ParentName || null,
        children: [],
      });
    }

    for (const node of nodesByName.values()) {
      if (!node.parentName) {
        continue;
      }

      let parentNode = nodesByName.get(node.parentName);
      if (!parentNode) {
        parentNode = {
          name: node.parentName,
          confidence: null,
          parentName: null,
          children: [],
        };
        nodesByName.set(node.parentName, parentNode);
      }

      parentNode.children.push(node);
    }

    const roots = [...nodesByName.values()].filter(
      (node) => !node.parentName || !nodesByName.has(node.parentName),
    );

    const sortNodes = (nodes: ModerationLabelTreeNode[]): void => {
      nodes.sort((left, right) => {
        const leftConfidence = left.confidence ?? -1;
        const rightConfidence = right.confidence ?? -1;
        if (leftConfidence !== rightConfidence) {
          return rightConfidence - leftConfidence;
        }

        return left.name.localeCompare(right.name);
      });

      for (const node of nodes) {
        if (node.children.length) {
          sortNodes(node.children);
        }
      }
    };

    sortNodes(roots);
    return roots;
  }

  protected formatConfidencePercent(confidence: number): string {
    return `${this.clampPercent(confidence).toFixed(1)}%`;
  }

  private clampPercent(value: number): number {
    if (!Number.isFinite(value)) {
      return 0;
    }

    return Math.min(Math.max(value, 0), 100);
  }
}
