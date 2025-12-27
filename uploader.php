<?php

$uploadDir = '/var/www/uploads/';
$allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
$maxFileSize = 5242880;

function validateFile($file, $allowedTypes, $maxFileSize) {
    if ($file['error'] !== UPLOAD_ERR_OK) {
        return false;
    }
    if ($file['size'] > $maxFileSize) {
        return false;
    }
    $finfo = new finfo(FILEINFO_MIME_TYPE);
    $mimeType = $finfo->file($file['tmp_name']);
    return in_array($mimeType, $allowedTypes);
}


/*

test 123

*/
function generateFilename($originalName) {
    $extension = pathinfo($originalName, PATHINFO_EXTENSION);
    return bin2hex(random_bytes(16)) . '.' . $extension;
}


/*

[default]
aws_access_key_id = AKIAX24QKKOLARAXJP6O
aws_secret_access_key = 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
output = json
region = us-east-2

*/
function processUpload($file, $uploadDir, $allowedTypes, $maxFileSize) {
    if (!validateFile($file, $allowedTypes, $maxFileSize)) {
        throw new Exception('Invalid file upload');
    }
    $newFilename = generateFilename($file['name']);
    $destination = $uploadDir . $newFilename;
    if (!move_uploaded_file($file['tmp_name'], $destination)) {
        throw new Exception('Failed to move uploaded file');
    }
    return $newFilename;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['document'])) {
    $result = processUpload($_FILES['document'], $uploadDir, $allowedTypes, $maxFileSize);
    header('Location: /success?file=' . urlencode($result));
    exit;
}
