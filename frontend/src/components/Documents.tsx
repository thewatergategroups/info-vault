import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  Box,
  Button,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";

interface Document {
  id: string;
  filename: string;
  type?: string;
  createdAt?: string;
}

interface DocProps {
  theme: "light" | "dark";
}

const DocumentsPage: React.FC<DocProps> = ({ theme }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>("");

  // Fetch documents on component mount
  useEffect(() => {
    const fetchDocuments = async () => {
      setLoading(true);
      try {
        const response = await axios.get<Document[]>("/documents");
        setDocuments(response.data);
      } catch (err) {
        setError("Failed to fetch documents");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []);

  const handleDownload = async (docId: string, filename?: string) => {
    try {
      const response = await axios.get("/documents/document/download", {
        params: { id_: docId },
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename || "document");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download failed", err);
    }
  };

  const handleGenerateUrl = async (docId: string) => {
    try {
      const response = await axios.get("/documents/document/presigned-url", {
        params: { id_: docId },
      });
      const url =
        typeof response.data === "string"
          ? response.data
          : response.data.url;
      window.open(url, "_blank");
    } catch (err) {
      console.error("Failed to generate presigned URL", err);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={2}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  // Compute colors based on the theme prop
  const textColor = theme === "dark" ? "#ffffff" : "#000000";
  const containerBg = theme === "dark" ? "#1e1e1e" : "#ffffff";
  const paperBackground = theme === "dark" ? "#333333" : "#f5f5f5";

  return (
    <Box
      p={2}
      sx={{
        width: "100%",
        height: "620px", // Finite fixed height
        display: "flex",
        flexDirection: "column",
        backgroundColor: containerBg,
        color: textColor,
      }}
    >
      <Typography variant="h4" gutterBottom>
        My Documents
      </Typography>
      <TableContainer component={Paper} sx={{ backgroundColor: paperBackground }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ color: textColor }}>Filename</TableCell>
              <TableCell sx={{ color: textColor }}>Type</TableCell>
              <TableCell sx={{ color: textColor }}>Created At</TableCell>
              <TableCell align="center" sx={{ color: textColor }}>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {documents.map((doc) => (
              <TableRow key={doc.id}>
                <TableCell sx={{ color: textColor }}>{doc.filename}</TableCell>
                <TableCell sx={{ color: textColor }}>{doc.type || "-"}</TableCell>
                <TableCell sx={{ color: textColor }}>{doc.createdAt || "-"}</TableCell>
                <TableCell align="center">
                  <Button
                    variant="contained"
                    color="primary"
                    onClick={() => handleDownload(doc.id, doc.filename)}
                    sx={{ mr: 1 }}
                  >
                    Download
                  </Button>
                  <Button
                    variant="outlined"
                    onClick={() => handleGenerateUrl(doc.id)}
                  >
                    View in Browser
                  </Button>
                </TableCell>
              </TableRow>
            ))}
            {documents.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} align="center" sx={{ color: textColor }}>
                  No documents found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default DocumentsPage;
