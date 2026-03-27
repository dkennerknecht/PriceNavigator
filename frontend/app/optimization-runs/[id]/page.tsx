"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { OptimizationResultView } from "@/components/optimization-result-view";
import { PageHeader } from "@/components/page-header";
import { apiClient } from "@/lib/api";
import type { OptimizationRun } from "@/lib/types";

export default function OptimizationRunDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [run, setRun] = useState<OptimizationRun | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .getOptimizationRun(Number(params.id))
      .then(setRun)
      .catch((caughtError) =>
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Optimierungslauf konnte nicht geladen werden.",
        ),
      );
  }, [params.id]);

  async function deleteRun() {
    if (!run || !window.confirm("Optimierungslauf löschen?")) {
      return;
    }
    await apiClient.deleteOptimizationRun(run.id);
    router.push("/shopping-lists");
  }

  return (
    <div className="page">
      <PageHeader
        title={run ? `Optimierung #${run.id}` : "Optimierung"}
        description="Shop-gruppiertes Ergebnis der deterministischen Shop-Penalty-Heuristik."
      />
      {error ? <p className="error-text">{error}</p> : null}
      {run ? (
        <>
          <div className="page-actions">
            <button className="button button-danger" type="button" onClick={() => void deleteRun()}>
              Lauf löschen
            </button>
          </div>
          <OptimizationResultView run={run} />
        </>
      ) : (
        <p className="muted">Lade Laufdaten ...</p>
      )}
    </div>
  );
}

