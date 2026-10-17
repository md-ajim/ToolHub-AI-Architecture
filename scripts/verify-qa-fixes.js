#!/usr/bin/env node
/**
 * Manual verification script for ToolHub AI Editor QA fixes.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
let passed = 0;
let failed = 0;

function check(description, condition) {
  if (condition) {
    console.log(`  PASS: ${description}`);
    passed++;
  } else {
    console.log(`  FAIL: ${description}`);
    failed++;
  }
}

function fileContains(filePath, text) {
  const full = path.join(ROOT, filePath);
  if (!fs.existsSync(full)) return false;
  return fs.readFileSync(full, 'utf-8').includes(text);
}

console.log('\n=== ToolHub AI QA Fix Verification ===\n');

// 1. Backend AI tools no longer mock
console.log('1. AI Backend Processing');
check('ai_tools/tasks.py uses PIL Image',
  fileContains('backend/apps/ai_tools/tasks.py', 'from PIL import'));
check('ai_tools/tasks.py has background-remove processing',
  fileContains('backend/apps/ai_tools/tasks.py', '_process_background_remove'));
check('ai_tasks.py has upscale processing',
  fileContains('backend/apps/ai_tools/tasks.py', '_process_upscale'));
check('ai_tasks.py has enhance processing',
  fileContains('backend/apps/ai_tools/tasks.py', '_process_enhance'));
check('ai_tasks.py has passport processing',
  fileContains('backend/apps/ai_tools/tasks.py', '_process_passport'));
check('ai_tasks.py has object-remove processing',
  fileContains('backend/apps/ai_tools/tasks.py', '_process_object_remove'));
check('Old mock sleep/copy removed from ai_tasks.py',
  !fileContains('backend/apps/ai_tools/tasks.py', 'time.sleep(5)'));

// 2. Backend image services fixes
console.log('\n2. Image Processing Fixes');
check('services.py normalizes EXIF orientation',
  fileContains('backend/apps/image_tools/services.py', 'exif_transpose'));
check('services.py captures format BEFORE transforms',
  fileContains('backend/apps/image_tools/services.py', '_get_format_and_mode'));
check('services.py preserves alpha for WebP/AVIF',
  fileContains('backend/apps/image_tools/services.py', '_prepare_for_format'));
check('services.py fixes watermark args (removed position)',
  fileContains('backend/apps/image_tools/services.py', 'def watermark_image(image_file, text'));
check('services.py has product-image service',
  fileContains('backend/apps/image_tools/services.py', 'def product_image'));
check('services.py has mockup service',
  fileContains('backend/apps/image_tools/services.py', 'def mockup_generator'));
check('services.py has flip service',
  fileContains('backend/apps/image_tools/services.py', 'def flip_image'));

// 3. Backend security
console.log('\n3. Backend Security');
check('image views use IsAuthenticated for job status',
  fileContains('backend/apps/image_tools/views.py', 'permission_classes = [IsAuthenticated]'));
check('ai views use IsAuthenticated for job status',
  fileContains('backend/apps/ai_tools/views.py', 'permission_classes = [IsAuthenticated]'));
check('image job status checks ownership',
  fileContains('backend/apps/image_tools/views.py', 'if job.user != request.user'));
check('ai job status checks ownership',
  fileContains('backend/apps/ai_tools/views.py', 'if job.user != request.user'));
check('exceptions.py does not expose raw str(e)',
  fileContains('backend/shared/exceptions.py', 'An internal server error occurred'));

// 4. Frontend API safety
console.log('\n4. Frontend API Safety');
check('authApi uses safeJson parsing',
  fileContains('frontend/src/features/auth/services/authApi.ts', 'safeJson'));
check('api.ts refresh checks Content-Type before JSON parse',
  fileContains('frontend/src/lib/api.ts', 'contentType.includes'));

// 5. EditorContext fixes
console.log('\n5. Editor State Fixes');
check('EditorContext applyResult handles http(s) URLs',
  fileContains('frontend/src/components/editor/EditorContext.tsx', 'url.startsWith("http")'));
check('EditorContext applyResult rebuilds File from http(s)',
  fileContains('frontend/src/components/editor/EditorContext.tsx', 'resultFile = new File'));
check('Undo/redo uses functional state updates',
  fileContains('frontend/src/components/editor/EditorContext.tsx', 'setHistoryIndex((prev) =>'));

// 6. useEditorOperation fixes
console.log('\n6. Operation Runner Fixes');
check('useEditorOperation clears ticker on failure path',
  fileContains('frontend/src/components/editor/useEditorOperation.ts',
    'window.clearInterval(ticker);\n          setProcessing('));

// 7. Export pipeline
console.log('\n7. Export Pipeline');
check('ExportDialog uses canvas re-encode for download',
  fileContains('frontend/src/components/editor/ExportDialog.tsx', 'canvas.toBlob'));
check('ExportDialog sanitizes filename',
  fileContains('frontend/src/components/editor/ExportDialog.tsx', 'replace(/[^a-zA-Z0-9_'));
check('ExportDialog handles JPEG background fill',
  fileContains('frontend/src/components/editor/ExportDialog.tsx', 'ctx.fillStyle = "#FFFFFF"'));

// 8. Inspector destructuring fix
console.log('\n8. Inspector Fixes');
check('ResizeInspector destructures runOperation correctly',
  fileContains('frontend/src/components/editor/EditorInspector.tsx',
    'const { runOperation, isRunning } = useEditorOperation();'));
check('ResizeInspector button disabled during processing',
  fileContains('frontend/src/components/editor/EditorInspector.tsx',
    'disabled={disabled}'));
check('ProductImageInspector uses real operation',
  fileContains('frontend/src/components/editor/EditorInspector.tsx',
    'ImageService.productImage'));
check('MockupInspector uses real operation',
  fileContains('frontend/src/components/editor/EditorInspector.tsx',
    'ImageService.mockupGenerate'));

// 9. Theme fixes
console.log('\n9. Theme / Accessibility');
check('BeforeAfter uses theme-aware colors instead of hardcoded white',
  fileContains('frontend/src/components/editor/EditorBeforeAfter.tsx', 'bg-foreground'));
check('CanvasInteraction uses CSS variables for handles',
  fileContains('frontend/src/components/editor/canvas/CanvasInteraction.tsx', 'var(--background)'));
check('EditorHeader has aria-labels on icon buttons',
  fileContains('frontend/src/components/editor/EditorHeader.tsx', 'aria-label'));

// 10. Backend URL routes
console.log('\n10. Backend Routes');
check('product-image endpoint exists',
  fileContains('backend/apps/image_tools/urls.py', 'product-image/'));
check('mockup endpoint exists',
  fileContains('backend/apps/image_tools/urls.py', 'mockup/'));
check('flip endpoint exists',
  fileContains('backend/apps/image_tools/urls.py', 'flip/'));

console.log('\n=== Results ===');
console.log(`Passed: ${passed}`);
console.log(`Failed: ${failed}`);
console.log(`Total:  ${passed + failed}`);

if (failed > 0) {
  console.log('\nSome checks failed. Review the output above.');
  process.exit(1);
} else {
  console.log('\nAll static verification checks passed.');
  process.exit(0);
}
