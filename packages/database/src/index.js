export function createLocalEnterpriseRepository(seed) {
  const requests = new Map(seed.map((request) => [request.id, structuredClone(request)]));
  const audit = [];
  return {
    listRequests(tenantId) {
      return Array.from(requests.values()).filter((request) => request.tenantId === tenantId).map((request) => structuredClone(request));
    },
    getRequest(tenantId, requestId) {
      const request = requests.get(requestId);
      return request?.tenantId === tenantId ? structuredClone(request) : null;
    },
    saveRequest(request, event) {
      if (request.tenantId !== event.tenantId || request.id !== event.requestId) {
        throw new Error("Repository refused an audit event outside the request boundary.");
      }
      requests.set(request.id, structuredClone(request));
      audit.push(structuredClone(event));
    },
    listAudit(tenantId, requestId) {
      return audit.filter((event) => event.tenantId === tenantId && event.requestId === requestId).map((event) => structuredClone(event));
    },
  };
}
