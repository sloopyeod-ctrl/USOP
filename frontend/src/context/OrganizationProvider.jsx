import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import api from "../api/usopApi";
import OrganizationContext from "./ActiveOrganizationContext";


const ACTIVE_ORGANIZATION_STORAGE_KEY =
  "usop.activeOrganizationId";


function resolveActiveOrganizationId(
  organizations,
) {
  const persistedOrganizationId =
    localStorage.getItem(
      ACTIVE_ORGANIZATION_STORAGE_KEY,
    );

  const persistedOrganizationExists =
    organizations.some(
      (organization) =>
        organization.id
        === persistedOrganizationId,
    );

  if (persistedOrganizationExists) {
    return persistedOrganizationId;
  }

  if (organizations.length === 1) {
    return organizations[0].id;
  }

  return "";
}


function persistActiveOrganizationId(
  organizationId,
) {
  if (organizationId) {
    localStorage.setItem(
      ACTIVE_ORGANIZATION_STORAGE_KEY,
      organizationId,
    );

    return;
  }

  localStorage.removeItem(
    ACTIVE_ORGANIZATION_STORAGE_KEY,
  );
}


export default function OrganizationProvider({
  children,
}) {
  const [organizations, setOrganizations] =
    useState([]);

  const [
    activeOrganizationId,
    setActiveOrganizationIdState,
  ] = useState("");

  const [
    isLoadingOrganizations,
    setIsLoadingOrganizations,
  ] = useState(true);

  const [
    organizationError,
    setOrganizationError,
  ] = useState(null);


  const applyOrganizations = useCallback(
    (records) => {
      const normalizedRecords =
        Array.isArray(records)
          ? records
          : [];

      const resolvedOrganizationId =
        resolveActiveOrganizationId(
          normalizedRecords,
        );

      setOrganizations(normalizedRecords);

      setActiveOrganizationIdState(
        resolvedOrganizationId,
      );

      persistActiveOrganizationId(
        resolvedOrganizationId,
      );
    },
    [],
  );


  useEffect(() => {
    let isCurrent = true;

    api
      .get("/api/v1/organizations/")
      .then((response) => {
        if (!isCurrent) {
          return;
        }

        applyOrganizations(response.data);
        setOrganizationError(null);
      })
      .catch((error) => {
        if (!isCurrent) {
          return;
        }

        console.error(
          "Organization context load failed:",
          error,
        );

        setOrganizations([]);
        setActiveOrganizationIdState("");
        persistActiveOrganizationId("");

        setOrganizationError(
          "Could not load Organization context.",
        );
      })
      .finally(() => {
        if (isCurrent) {
          setIsLoadingOrganizations(false);
        }
      });

    return () => {
      isCurrent = false;
    };
  }, [applyOrganizations]);


  const reloadOrganizations = useCallback(
    async () => {
      setIsLoadingOrganizations(true);
      setOrganizationError(null);

      try {
        const response = await api.get(
          "/api/v1/organizations/",
        );

        applyOrganizations(response.data);
      } catch (error) {
        console.error(
          "Organization context reload failed:",
          error,
        );

        setOrganizationError(
          "Could not load Organization context.",
        );
      } finally {
        setIsLoadingOrganizations(false);
      }
    },
    [applyOrganizations],
  );


  const setActiveOrganizationId =
    useCallback(
      (organizationId) => {
        const normalizedOrganizationId =
          organizationId || "";

        const organizationExists =
          organizations.some(
            (organization) =>
              organization.id
              === normalizedOrganizationId,
          );

        const validOrganizationId =
          organizationExists
            ? normalizedOrganizationId
            : "";

        setActiveOrganizationIdState(
          validOrganizationId,
        );

        persistActiveOrganizationId(
          validOrganizationId,
        );
      },
      [organizations],
    );


  const activeOrganization = useMemo(
    () =>
      organizations.find(
        (organization) =>
          organization.id
          === activeOrganizationId,
      ) || null,
    [
      organizations,
      activeOrganizationId,
    ],
  );


  const value = useMemo(
    () => ({
      organizations,
      activeOrganization,
      activeOrganizationId,
      setActiveOrganizationId,
      isLoadingOrganizations,
      organizationError,
      reloadOrganizations,
    }),
    [
      organizations,
      activeOrganization,
      activeOrganizationId,
      setActiveOrganizationId,
      isLoadingOrganizations,
      organizationError,
      reloadOrganizations,
    ],
  );


  return (
    <OrganizationContext.Provider
      value={value}
    >
      {children}
    </OrganizationContext.Provider>
  );
}