import { inject } from '@angular/core';
import { MatIconRegistry } from '@angular/material/icon';
import { DomSanitizer } from '@angular/platform-browser';

interface IconDefinition {
  name: string;
  path: string;
}

export function initIcons() {
  const iconRegistry = inject(MatIconRegistry);
  const sanitizer = inject(DomSanitizer);

  const ICONS: IconDefinition[] = [
    { name: 'github', path: 'icons/github.svg' },
    { name: 'linkedin', path: 'icons/linkedin.svg' },
  ];

  ICONS.forEach((icon) => {
    iconRegistry.addSvgIcon(icon.name, sanitizer.bypassSecurityTrustResourceUrl(icon.path));
  });
}
